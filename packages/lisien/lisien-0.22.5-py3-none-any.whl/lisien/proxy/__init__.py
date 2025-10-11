# This file is part of Lisien, a framework for life simulation games.
# Copyright (c) Zachary Spector, public@zacharyspector.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""Proxy objects to access lisien entities from another process.

Each proxy class is meant to emulate the equivalent lisien class,
and any change you make to a proxy will be made in the corresponding
entity in the lisien core.

To use these, first instantiate an ``EngineProcessManager``, then
call its ``start`` method with the same arguments you'd give a real
``Engine``. You'll get an ``EngineProxy``, which acts like the underlying
``Engine`` for most purposes.

"""

from __future__ import annotations

import ast
import io
import logging
import os
import pickle
import random
import sys
import zlib
from abc import ABC, abstractmethod
from ast import unparse
from collections import UserDict
from collections.abc import Mapping, MutableMapping, MutableSequence
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from functools import cached_property, partial
from inspect import getsource
from multiprocessing.connection import Connection
from queue import Queue, SimpleQueue
from random import Random
from threading import Lock, Thread
from time import monotonic
from types import MethodType
from typing import Hashable, Iterable, Iterator, Literal, Optional

import msgpack
import networkx as nx
import tblib
from blinker import Signal

from ..cache import PickyDefaultDict, StructuredDefaultDict
from ..collections import (
	AbstractLanguageDescriptor,
	FunctionStore,
	StringStore,
)
from ..exc import (
	AmbiguousLeaderError,
	OutOfTimelineError,
	WorkerProcessReadOnlyError,
)
from ..facade import CharacterFacade
from ..node import Place, Thing
from ..portal import Portal
from ..types import (
	ActionFuncName,
	Branch,
	CharDelta,
	CharName,
	DeltaDict,
	Edge,
	EdgesDict,
	EdgeValDict,
	EternalKey,
	FuncName,
	FuncStoreName,
	Key,
	Keyframe,
	Node,
	NodeName,
	NodesDict,
	NodeValDict,
	PrereqFuncName,
	RulebookName,
	RulebookPriority,
	RuleFuncName,
	RuleName,
	RuleNeighborhood,
	Stat,
	StatDict,
	Tick,
	Time,
	TriggerFuncName,
	Turn,
	UniversalKey,
	Value,
)
from ..util import (
	AbstractBookmarkMapping,
	AbstractCharacter,
	AbstractEngine,
	MsgpackExtensionType,
	TimeSignalDescriptor,
	getatt,
	repr_call_sig,
)
from ..wrap import (
	DictWrapper,
	ListWrapper,
	OrderlyFrozenSet,
	OrderlySet,
	SetWrapper,
	UnwrappingDict,
)
from .handle import EngineHandle


class CachingProxy(MutableMapping, Signal):
	"""Abstract class for proxies to lisien entities or mappings thereof"""

	_cache: dict
	rulebook: RuleBookProxy
	engine: EngineProxy

	def _worker_check(self):
		self.engine._worker_check()

	def __init__(self):
		super().__init__()
		self.exists = True

	def __bool__(self):
		return bool(self.exists)

	def __iter__(self):
		yield from self._cache

	def __len__(self):
		return len(self._cache)

	def __contains__(self, k: Key) -> bool:
		return k in self._cache

	def __getitem__(self, k: Key) -> Value:
		if k not in self:
			raise KeyError("No such key: {}".format(k))
		return self._cache_get_munge(k, self._cache[k])

	def setdefault(self, k: Key, default: Value = None) -> Value:
		if k not in self:
			if default is None:
				raise KeyError("No such key", k)
			self[k] = default
			return default
		return self[k]

	def __setitem__(self, k: Key, v: Value) -> None:
		self._worker_check()
		self._set_item(k, v)
		self._cache[k] = self._cache_set_munge(k, v)
		self.send(self, key=k, value=v)

	def __delitem__(self, k: Key) -> None:
		self._worker_check()
		if k not in self:
			raise KeyError("No such key: {}".format(k))
		self._del_item(k)
		if k in self._cache:
			del self._cache[k]
		self.send(self, key=k, value=None)

	@abstractmethod
	def _apply_delta(self, delta):
		raise NotImplementedError("_apply_delta")

	def _cache_get_munge(self, k: Key, v: Value) -> Value:
		return v

	def _cache_set_munge(self, k: Key, v: Value) -> Value:
		return v

	@abstractmethod
	def _set_item(self, k: Key, v: Value) -> None:
		raise NotImplementedError("Abstract method")

	@abstractmethod
	def _del_item(self, k: Key) -> None:
		raise NotImplementedError("Abstract method")


class CachingEntityProxy(CachingProxy):
	"""Abstract class for proxy objects representing lisien entities"""

	name: Hashable

	def _cache_get_munge(self, k: Key, v: Value) -> Value:
		if isinstance(v, dict):
			return DictWrapper(lambda: self._cache[k], self, k)
		elif isinstance(v, list):
			return ListWrapper(lambda: self._cache[k], self, k)
		elif isinstance(v, set):
			return SetWrapper(lambda: self._cache[k], self, k)
		return v

	def __repr__(self):
		return "<{}({}) {} at {}>".format(
			self.__class__.__name__, self._cache, self.name, id(self)
		)


class RuleMapProxy(MutableMapping, Signal):
	@property
	def _cache(self) -> list[RuleName]:
		no_rules: list[RuleName] = []
		zero_prio = RulebookPriority(0.0)
		return self.engine._rulebooks_cache.setdefault(
			self.name, (no_rules, zero_prio)
		)[0]

	@property
	def priority(self) -> RulebookPriority:
		no_rules: list[RuleName] = []
		zero_prio = RulebookPriority(0.0)
		return self.engine._rulebooks_cache.setdefault(
			self.name, (no_rules, zero_prio)
		)[1]

	@priority.setter
	def priority(self, v: RulebookPriority):
		self.engine.handle(
			"set_rulebook_priority", rulebook=self.name, priority=v
		)
		if self.name in self.engine._rulebooks_cache:
			rules, _ = self.engine._rulebooks_cache[self.name]
			self.engine._rulebooks_cache[self.name] = (rules, v)
		else:
			self.engine._rulebooks_cache[self.name] = ([], v)

	@property
	def engine(self) -> EngineProxy:
		return self.entity.engine

	def _worker_check(self) -> None:
		self.engine._worker_check()

	def __init__(
		self,
		entity: CharacterProxy | ThingProxy | PlaceProxy | PortalProxy,
		rulebook_name: RulebookName,
	):
		super().__init__()
		self.entity = entity
		self.name = rulebook_name
		self._proxy_cache = entity.engine._rule_obj_cache

	def __iter__(self) -> Iterator[RuleName]:
		return iter(self._cache)

	def __len__(self) -> int:
		return len(self._cache)

	def __call__(
		self,
		action: FuncName | callable | FuncProxy | None = None,
		always: bool = False,
		neighborhood: Optional[RuleNeighborhood] = None,
	) -> callable | RuleProxy:
		if action is None:
			return partial(self, always=always, neighborhood=neighborhood)
		self._worker_check()
		if isinstance(action, FuncProxy):
			rule_name = RuleName(action.name)
			self[rule_name] = [action.name]
		else:
			if callable(action):
				self.engine.action(action)
				action = action.__name__
			self[action] = [action]
		ret = self[action]
		if neighborhood is not None:
			ret.neighborhood = neighborhood
		if always:
			ret.triggers.append(self.engine.trigger.truth)
		return ret

	def __getitem__(self, key: RuleName) -> RuleProxy:
		if key in self._cache:
			if key not in self._proxy_cache:
				self._proxy_cache[key] = RuleProxy(self.engine, key)
			return self._proxy_cache[key]
		raise KeyError("Rule not assigned to rulebook", key, self.name)

	def __setitem__(
		self, k: RuleName, v: RuleProxy | list[FuncProxy | RuleFuncName]
	):
		self._worker_check()
		if self.name not in self.engine._rulebooks_cache:
			self.engine.handle("new_empty_rulebook", rulebook=self.name)
			self.engine._rulebooks_cache[self.name] = ([], 0.0)
			self.entity._set_rulebook_name(self.name)
		if isinstance(v, RuleProxy):
			v = v._name
		else:
			if k not in self.engine._rule_obj_cache:
				rp = self.engine._rule_obj_cache[k] = RuleProxy(self.engine, k)
			else:
				rp = self.engine._rule_obj_cache[k]
			rp.actions = v
			v = k
		if k in self._cache:
			return
		i = len(self._cache)
		self._cache.append(k)
		self.engine.handle(
			command="set_rulebook_rule",
			rulebook=self.name,
			i=i,
			rule=v,
			branching=True,
		)
		self.send(self, key=k, val=v)

	def __delitem__(self, key: RuleName):
		self._worker_check()
		i = self._cache.index(key)
		if i is None:
			raise KeyError("Rule not set in rulebook", key, self.name)
		del self._cache[i]
		self.engine.handle(
			command="del_rulebook_rule",
			rulebook=self.name,
			i=i,
			branching=True,
		)
		self.send(self, key=key, val=None)


class RuleFollowerProxyDescriptor:
	def __set__(self, inst, val: RuleBookProxy | RuleMapProxy):
		inst.engine._worker_check()
		if isinstance(val, RuleBookProxy):
			rb = val
			val = val.name
		elif isinstance(val, RuleMapProxy):
			if val.name in inst.engine._rulebooks_cache:
				rb = inst.engine._rulebooks_cache[val.name]
				val = val.name
			else:
				rb = inst.engine._rulebooks_cache[val.name] = RuleBookProxy(
					inst.engine, val.name
				)
				val = val.name
		inst._set_rulebook_name(val)
		if hasattr(inst, "send"):
			inst.send(inst, rulebook=val)


class RuleMapProxyDescriptor(RuleFollowerProxyDescriptor):
	def __get__(self, instance, owner):
		if instance is None:
			return self
		if hasattr(instance, "_rule_map_proxy"):
			return instance._rule_map_proxy
		else:
			try:
				name = instance._get_rulebook_name()
			except KeyError:
				name = instance._get_default_rulebook_name()
			proxy = instance._rule_map_proxy = RuleMapProxy(instance, name)
		return proxy


class RulebookProxyDescriptor(RuleFollowerProxyDescriptor):
	"""Descriptor that makes the corresponding RuleBookProxy if needed"""

	def __get__(self, inst, cls):
		if inst is None:
			return self
		return inst._get_rulebook_proxy()


class ProxyLeaderMapping(Mapping):
	"""A mapping to the ``CharacterProxy``s that have this node as a unit"""

	def __init__(self, node: NodeProxy):
		self.node = node

	def __iter__(self):
		try:
			return iter(self._user_names())
		except KeyError:
			return iter(())

	def __len__(self):
		try:
			return len(self._user_names())
		except KeyError:
			return 0

	def __contains__(self, item: CharName) -> bool:
		try:
			return item in self._user_names()
		except KeyError:
			return False

	def __getitem__(self, item: CharName):
		if item not in self:
			raise KeyError("Not a leader of this node", item, self.node.name)
		return self.node.engine.character[item]

	@property
	def only(self):
		if len(self) == 1:
			return next(iter(self.values()))
		raise AmbiguousLeaderError("No leaders, or more than one")

	def _user_names(self):
		return self.node.engine._unit_characters_cache[self.node._charname][
			self.node.name
		]


class ProxyNeighborMapping(Mapping):
	__slots__ = ("_node",)

	def __init__(self, node: NodeProxy) -> None:
		self._node = node

	def __iter__(self) -> Iterator[NodeName]:
		seen = set()
		for k in self._node.character.adj[self._node.name]:
			yield k
			seen.add(k)
		for k in self._node.character.pred[self._node.name]:
			if k not in seen:
				yield k

	def __len__(self) -> int:
		return len(
			self._node.character.adj[self._node.name].keys()
			| self._node.character.pred[self._node.name].keys()
		)

	def __getitem__(self, item: NodeName) -> NodeProxy:
		if (
			item in self._node.character.adj[self._node.name]
			or item in self._node.character.pred[self._node.name]
		):
			return self._node.character.node[item]
		raise KeyError("Not a neighbor")


class RuleFollowerProxy(ABC):
	rule = RuleMapProxyDescriptor()
	rulebook = RulebookProxyDescriptor()
	engine: EngineProxy

	@abstractmethod
	def _get_default_rulebook_name(self) -> RulebookName:
		pass

	@abstractmethod
	def _get_rulebook_name(self) -> RulebookName:
		pass

	def _worker_check(self):
		self.engine._worker_check()

	def _get_rulebook_proxy(self) -> RuleBookProxy:
		try:
			name = self._get_rulebook_name()
		except KeyError:
			name = self._get_default_rulebook_name()
		if name not in self.engine._rulebook_obj_cache:
			self.engine._rulebook_obj_cache[name] = RuleBookProxy(
				self.engine, name
			)
		return self.engine._rulebook_obj_cache[name]

	@abstractmethod
	def _set_rulebook_name(self, rb: RulebookName) -> None:
		pass


class NodeContentProxy(Mapping):
	def __init__(self, node: NodeProxy):
		self.node = node

	def __getitem__(self, key: NodeName, /):
		if key not in self.node.character.thing:
			raise KeyError("No such thing", key, self.node.character.name)
		thing = self.node.character.thing[key]
		if thing.location != self.node:
			raise KeyError(
				"Not located here",
				key,
				self.node.character.name,
				self.node.name,
			)
		return thing

	def __len__(self):
		n = 0
		for _ in self:
			n += 1
		return n

	def __iter__(self) -> Iterator[NodeName]:
		return self.node.engine._node_contents(
			self.node.character.name, self.node.name
		)

	def __contains__(self, item: NodeName):
		return (
			item in self.node.character.thing
			and self.node.character.thing[item].location == self.node
		)


class NodePortalProxy(Mapping):
	def __init__(self, node):
		self.node = node

	def __getitem__(self, key: NodeName, /) -> PortalProxy:
		return self.node.character.portal[self.node.name][key]

	def __len__(self):
		try:
			return len(self.node.character.portal[self.node.name])
		except KeyError:
			return 0

	def __iter__(self):
		return iter(self.node.character.portal[self.node.name])


class NodePreportalProxy(Mapping):
	def __init__(self, node: NodeProxy):
		self.node = node

	def __getitem__(self, key: NodeName, /) -> PortalProxy:
		return self.node.engine._character_portals_cache.predecessors[
			self.node.character.name
		][self.node.name][key]

	def __len__(self):
		try:
			return len(
				self.node.engine._character_portals_cache.predecessors[
					self.node.character.name
				][self.node.name]
			)
		except KeyError:
			return 0

	def __iter__(self) -> Iterator[NodeName]:
		return iter(
			self.node.engine._character_portals_cache.predecessors[
				self.node.character.name
			][self.node.name]
		)


class NodeProxy(CachingEntityProxy, RuleFollowerProxy):
	name: NodeName

	@property
	def graph(self) -> CharacterProxy:
		return self.character

	@property
	def leader(self) -> ProxyLeaderMapping:
		return ProxyLeaderMapping(self)

	@property
	def character(self) -> CharacterProxy:
		return self.engine.character[self._charname]

	@property
	def _cache(self):
		return self.engine._node_stat_cache[self._charname][self.name]

	def _get_default_rulebook_name(self):
		return self._charname, self.name

	def _get_rulebook_name(self):
		return self.engine._char_node_rulebooks_cache[self._charname][
			self.name
		]

	def _set_rulebook_name(self, rb: RulebookName):
		self.engine.handle(
			"set_node_rulebook",
			char=self._charname,
			node=self.name,
			rulebook=rb,
			branching=True,
		)
		self.engine._char_node_rulebooks_cache[self._charname][self.name] = rb

	def __init__(self, character: CharacterProxy, nodename: NodeName, **stats):
		self.engine = character.engine
		self._charname = character.name
		self.name = nodename
		self._cache.update(stats)
		super().__init__()

	def __eq__(self, other: NodeProxy):
		return (
			isinstance(other, NodeProxy)
			and self._charname == other._charname
			and self.name == other.name
		)

	def __contains__(self, k):
		if k in ("character", "name"):
			return True
		return super().__contains__(k)

	def __getitem__(self, k):
		if k == "character":
			return self._charname
		elif k == "name":
			return self.name
		return super().__getitem__(k)

	def _set_item(self, k: Key, v):
		if k == "name":
			raise KeyError("Nodes can't be renamed")
		self.engine.handle(
			command="set_node_stat",
			char=self._charname,
			node=self.name,
			k=k,
			v=v,
			branching=True,
		)

	def _del_item(self, k: Key):
		if k == "name":
			raise KeyError("Nodes need names")
		self.engine.handle(
			command="del_node_stat",
			char=self._charname,
			node=self.name,
			k=k,
			branching=True,
		)

	def delete(self):
		self._worker_check()
		self.engine.del_node(self._charname, self.name)

	@property
	def content(self):
		return NodeContentProxy(self)

	def contents(self):
		return self.content.values()

	@property
	def portal(self):
		return NodePortalProxy(self)

	def portals(self):
		return self.portal.values()

	@property
	def preportal(self):
		return NodePreportalProxy(self)

	def preportals(self):
		return self.preportal.values()

	@property
	def neighbor(self):
		return ProxyNeighborMapping(self)

	def neighbors(self):
		return self.neighbor.values()

	def add_thing(self, name: NodeName, **kwargs):
		return self.character.add_thing(name, self.name, **kwargs)

	def new_thing(self, name: NodeName, **kwargs):
		return self.character.new_thing(name, self.name, **kwargs)

	def add_portal(self, dest: NodeName, **kwargs):
		self.character.add_portal(self.name, dest, **kwargs)

	def new_portal(self, dest: NodeName, **kwargs):
		dest = getattr(dest, "name", dest)
		self.add_portal(dest, **kwargs)
		return self.character.portal[self.name][dest]

	def shortest_path(
		self, dest: NodeName | NodeProxy, weight: Key = None
	) -> list[NodeName]:
		"""Return a list of node names leading from me to ``dest``.

		Raise ``ValueError`` if ``dest`` is not a node in my character
		or the name of one.

		"""
		return nx.shortest_path(
			self.character, self.name, self._plain_dest_name(dest), weight
		)

	def _plain_dest_name(self, dest: NodeName | NodeProxy) -> NodeName:
		if isinstance(dest, NodeProxy):
			if dest.character != self.character:
				raise ValueError(
					"{} not in {}".format(dest.name, self.character.name)
				)
			return dest.name
		else:
			if dest in self.character.node:
				return dest
			raise ValueError("{} not in {}".format(dest, self.character.name))


class PlaceProxy(NodeProxy):
	def __repr__(self):
		return "<proxy to {}.place[{}] at {}>".format(
			self._charname, repr(self.name), id(self)
		)

	def _apply_delta(self, delta):
		for k, v in delta.items():
			if k == "rulebook":
				if k != self.rulebook.name:
					self.engine._char_node_rulebooks_cache[self._charname][
						self.name
					] = v
					self.send(self, key="rulebook", value=v)
					self.character.place.send(self, key="rulebook", value=v)
					self.character.node.send(self, key="rulebook", value=v)
				continue
			elif k == "location":
				if v is ...:
					if (
						self.character.name in self.engine._things_cache
						and self.name
						in self.engine._things_cache[self.character.name]
					):
						del self.engine._things_cache[self.character.name][
							self.name
						]
					self.engine._character_places_cache[self.character.name][
						self.name
					] = self
				else:
					self.engine._things_cache[self.character.name][
						self.name
					] = ThingProxy(self.character, self.name, v, **self._cache)
					del self.engine._character_places_cache[
						self.character.name
					][self.name]
				continue
			if v is ...:
				if k in self._cache:
					del self._cache[k]
					self.send(self, key=k, value=...)
					self.character.place.send(self, key=k, value=...)
					self.character.node.send(self, key=k, value=...)
			elif k not in self._cache or self._cache[k] != v:
				self._cache[k] = v
				self.send(self, key=k, value=v)
				self.character.place.send(self, key=k, value=v)
				self.character.node.send(self, key=k, value=v)


Place.register(PlaceProxy)


class ThingProxy(NodeProxy):
	@property
	def location(self) -> NodeProxy:
		return self.engine.character[self._charname].node[self._location]

	@location.setter
	def location(self, v: NodeProxy | NodeName | None):
		if isinstance(v, NodeProxy):
			if v.character != self.character:
				raise ValueError(
					"Things can only be located in their character. "
					"Maybe you want a unit?"
				)
			locn = v.name
		elif v in self.character.node or v is None:
			locn = v
		else:
			raise TypeError("Location must be a node or the name of one")
		self._set_location(locn)

	def __init__(
		self,
		character: CharacterProxy,
		name: NodeName,
		location: NodeName | None = None,
		**kwargs: StatDict,
	):
		if location is None and getattr(
			character.engine, "_initialized", True
		):
			raise ValueError("Thing must have location")
		super().__init__(character, name)
		self._location = location
		self._cache.update(kwargs)

	def __iter__(self):
		yield from super().__iter__()
		yield "location"

	def __getitem__(self, k: NodeName):
		if k == "location":
			return self._location
		return super().__getitem__(k)

	def _apply_delta(self, delta: StatDict):
		for k, v in delta.items():
			if k == "rulebook":
				if v is ...:
					cnrbc = self.engine._char_node_rulebooks_cache
					if (
						self._charname in cnrbc
						and self.name in cnrbc[self._charname]
					):
						del cnrbc[self._charname][self.name]
				elif v != self.rulebook.name:
					self.engine._char_node_rulebooks_cache[self._charname][
						self.name
					] = v
				if v != self.rulebook.name:
					self.send(self, key="rulebook", value=v)
					self.character.thing.send(self, key="rulebook", value=v)
					self.character.node.send(self, key="rulebook", value=v)
			elif v is ...:
				if k == "location":
					del self.engine._things_cache[self.character.name][
						self.name
					]
					self.engine._character_places_cache[self.character.name][
						self.name
					] = PlaceProxy(self.character, self.name, **self._cache)
					continue
				if k in self._cache:
					del self._cache[k]
					self.send(self, key=k, value=...)
					self.character.thing.send(self, key=k, value=...)
					self.character.node.send(self, key=k, value=...)
			elif k == "location":
				self._location = v
				self.send(self, key=k, value=v)
				self.character.thing.send(self, key=k, value=v)
				self.character.node.send(self, key=k, value=v)
			elif k not in self._cache or self._cache[k] != v:
				self._cache[k] = v
				self.send(self, key=k, value=v)
				self.character.thing.send(self, key=k, value=v)
				self.character.node.send(self, key=k, value=v)

	def _set_location(self, v: NodeName | ...):
		if v is ...:
			del self.engine._things_cache[self.character.name][self.name]
			self.engine._character_places_cache[self.character.name][
				self.name
			] = PlaceProxy(self.character, self.name, **self._cache)
		self._location = v
		self.engine.handle(
			command="set_thing_location",
			char=self.character.name,
			thing=self.name,
			loc=v,
			branching=True,
		)

	def __setitem__(self, k: Key, v: Value):
		self._worker_check()
		if k == "location":
			self._set_location(NodeName(Key(v)))
		elif k == "rulebook":
			self._set_rulebook_name(RulebookName(Key(v)))
		else:
			super().__setitem__(k, v)
		self.send(self, key=k, value=v)
		self.character.thing.send(self, key=k, value=v)
		self.character.node.send(self, key=k, value=v)

	def __repr__(self):
		return "<proxy to {}.thing[{}]@{} at {}>".format(
			self._charname, self.name, self._location, id(self)
		)

	def follow_path(self, path: list[NodeName], weight: Optional[Stat] = None):
		self._worker_check()
		self.engine.handle(
			command="thing_follow_path",
			char=self._charname,
			thing=self.name,
			path=path,
			weight=weight,
		)

	def go_to_place(
		self, place: NodeProxy | NodeName, weight: Optional[Stat] = None
	):
		self._worker_check()
		if hasattr(place, "name"):
			place = place.name
		self.engine.handle(
			command="thing_go_to_place",
			char=self._charname,
			thing=self.name,
			place=place,
			weight=weight,
		)

	def travel_to(
		self,
		dest: NodeProxy,
		weight: Optional[Stat] = None,
		graph: Optional[CharName] = None,
	):
		self._worker_check()
		if hasattr(dest, "name"):
			dest = dest.name
		if hasattr(graph, "name"):
			graph = graph.name
		return self.engine.handle(
			command="thing_travel_to",
			char=self._charname,
			thing=self.name,
			dest=dest,
			weight=weight,
			graph=graph,
		)

	def travel_to_by(
		self,
		dest: NodeProxy,
		arrival_tick: Tick,
		weight: Optional[Key] = None,
		graph: Optional[CharName] = None,
	):
		self._worker_check()
		if hasattr(dest, "name"):
			dest = dest.name
		if hasattr(graph, "name"):
			graph = graph.name
		self.engine.handle(
			command="thing_travel_to_by",
			char=self._charname,
			thing=self.name,
			dest=dest,
			arrival_tick=arrival_tick,
			weight=weight,
			graph=graph,
		)


Thing.register(ThingProxy)


class PortalProxy(CachingEntityProxy, RuleFollowerProxy):
	@property
	def orig(self):
		return self._origin

	@property
	def dest(self):
		return self._destination

	def _apply_delta(self, delta):
		for k, v in delta.items():
			if k == "rulebook":
				if v != self.rulebook.name:
					self.engine._char_port_rulebooks_cache[self._charname][
						self._origin
					][self._destination] = v
				continue
			if v is ...:
				if k in self._cache:
					del self._cache[k]
					self.send(self, key=k, value=...)
					self.character.portal.send(self, key=k, value=...)
			elif k not in self._cache or self._cache[k] != v:
				self._cache[k] = v
				self.send(self, key=k, value=v)
				self.character.portal.send(self, key=k, value=v)

	def _get_default_rulebook_name(self) -> RulebookName:
		return RulebookName(
			Key((self._charname, self._origin, self._destination))
		)

	def _get_rulebook_name(self) -> RulebookName:
		return self.engine._char_port_rulebooks_cache[self._charname][
			self._origin
		][self._destination]

	def _set_rulebook_name(self, rb: RulebookName) -> None:
		self.engine.handle(
			command="set_portal_rulebook",
			char=self._charname,
			orig=self._origin,
			dest=self._destination,
			rulebook=rb,
		)
		self.engine._char_port_rulebooks_cache[self._charname][self._origin][
			self._destination
		] = rb

	@property
	def _cache(self) -> StatDict:
		return self.engine._portal_stat_cache[self._charname][self._origin][
			self._destination
		]

	@property
	def character(self) -> CharacterProxy:
		return self.engine.character[self._charname]

	@property
	def graph(self) -> CharacterProxy:
		return self.engine.character[self._charname]

	@property
	def origin(self) -> NodeProxy:
		return self.character.node[self._origin]

	@property
	def destination(self) -> NodeProxy:
		return self.character.node[self._destination]

	@property
	def reciprocal(self) -> PortalProxy:
		if (
			self._origin not in self.character.pred
			or self._destination not in self.character.pred[self._origin]
		):
			return None
		return self.character.pred[self._origin][self._destination]

	def _set_item(self, k: Stat, v: Value) -> None:
		self.engine.handle(
			command="set_portal_stat",
			char=self._charname,
			orig=self._origin,
			dest=self._destination,
			k=k,
			v=v,
			branching=True,
		)
		self.send(self, k=k, v=v)
		self.character.portal.send(self, k=k, v=v)

	def _del_item(self, k: Stat) -> None:
		self.engine.handle(
			command="del_portal_stat",
			char=self._charname,
			orig=self._origin,
			dest=self._destination,
			k=k,
			branching=True,
		)
		self.character.portal.send(self, k=k, v=None)
		self.send(self, k=k, v=None)

	def __init__(
		self, character: CharacterProxy, origname: NodeName, destname: NodeName
	):
		self.engine = character.engine
		self._charname = character.name
		self._origin = origname
		self._destination = destname
		super().__init__()

	def __eq__(self, other: Edge):
		return (
			hasattr(other, "character")
			and hasattr(other, "origin")
			and hasattr(other, "destination")
			and self.character == other.character
			and self.origin == other.origin
			and self.destination == other.destination
		)

	def __repr__(self):
		return "<proxy to {}.portal[{}][{}] at {}>".format(
			self._charname,
			repr(self._origin),
			repr(self._destination),
			id(self),
		)

	def __getitem__(self, k: Stat) -> NodeName | CharName | Value:
		if k == "origin":
			return self._origin
		elif k == "destination":
			return self._destination
		elif k == "character":
			return self._charname
		return super().__getitem__(k)

	def delete(self) -> None:
		self._worker_check()
		self.engine.del_portal(self._charname, self._origin, self._destination)


Portal.register(PortalProxy)


class NodeMapProxy(MutableMapping, Signal):
	@property
	def character(self):
		return self.engine.character[self._charname]

	def __init__(self, engine_proxy: EngineProxy, charname: CharName):
		super().__init__()
		self.engine = engine_proxy
		self._charname = charname

	def __iter__(self):
		yield from self.character.thing
		yield from self.character.place

	def __len__(self):
		return len(self.character.thing) + len(self.character.place)

	def __getitem__(self, k: NodeName) -> ThingProxy | PlaceProxy:
		if k in self.character.thing:
			return self.character.thing[k]
		else:
			return self.character.place[k]

	def __setitem__(self, k: NodeName, v: StatDict) -> None:
		self.engine._worker_check()
		self.character.place[k] = v

	def __delitem__(self, k: NodeName) -> None:
		self.engine._worker_check()
		if k in self.character.thing:
			del self.character.thing[k]
		else:
			del self.character.place[k]

	def patch(self, patch: NodeValDict):
		"""Change a bunch of node stats at once.

		This works similarly to ``update``, but only accepts a dict-like
		argument, and it recurses one level.

		The patch is sent to the lisien core all at once, so this is faster than
		using ``update``, too.

		:param patch: a dictionary. Keys are node names, values are other dicts
		describing updates to the nodes, where a value of None means delete the
		stat. Other values overwrite.

		"""
		self.engine.handle(
			"update_nodes", char=self.character.name, patch=patch
		)
		for node, stats in patch.items():
			nodeproxycache = self[node]._cache
			for k, v in stats.items():
				if v is None:
					del nodeproxycache[k]
				else:
					nodeproxycache[k] = v


class ThingMapProxy(CachingProxy, RuleFollowerProxy):
	def _get_default_rulebook_name(self) -> RulebookName:
		return RulebookName(Key(("character_thing_rulebook", self.name)))

	def _get_rulebook_name(self) -> RulebookName:
		return self.engine._character_rulebooks_cache[self.name]["thing"]

	def _set_rulebook_name(self, rb: RulebookName) -> None:
		self.engine.handle(
			"set_character_thing_rulebook",
			char=self.name,
			rulebook=rb,
			branching=True,
		)
		self.engine._character_rulebooks_cache[self.name]["thing"] = rb

	def _apply_delta(self, delta: NodeValDict) -> None:
		raise NotImplementedError("_apply_delta")

	@property
	def character(self) -> CharacterProxy:
		return self.engine.character[self.name]

	@property
	def _cache(self):
		return self.engine._things_cache.setdefault(self.name, {})

	def __init__(self, engine_proxy: EngineProxy, charname: CharName):
		self.engine: EngineProxy = engine_proxy
		self.name: CharName = charname
		super().__init__()

	def __eq__(self, other):
		return self is other

	def _cache_set_munge(self, k: NodeName, v: StatDict):
		return ThingProxy(
			self.character,
			*self.engine.handle(
				"get_thing_special_stats", char=self.name, thing=k
			),
		)

	def _set_item(self, k: NodeName, v: StatDict):
		self.engine.handle(
			command="set_thing",
			char=self.name,
			thing=k,
			statdict=v,
			branching=True,
		)
		self._cache[k] = ThingProxy(
			self.character, k, NodeName(Key(v.pop("location")))
		)
		self.engine._node_stat_cache[self.name][k] = v

	def _del_item(self, k: Stat) -> None:
		self.engine.handle(
			command="del_node", char=self.name, node=k, branching=True
		)
		del self.engine._node_stat_cache[self.name][k]

	def patch(self, d: NodeValDict) -> None:
		self._worker_check()
		places = d.keys() & self.character.place.keys()
		if places:
			raise KeyError(f"Tried to patch places on thing mapping: {places}")
		self.character.node.patch(d)


class PlaceMapProxy(CachingProxy, RuleFollowerProxy):
	def _get_default_rulebook_name(self) -> RulebookName:
		return RulebookName(
			Key(
				(
					"character_place_rulebook",
					self.name,
				)
			)
		)

	def _get_rulebook_name(self) -> RulebookName:
		return self.engine._character_rulebooks_cache[self.name]["place"]

	def _set_rulebook_name(self, rb: RulebookName) -> None:
		self.engine.handle(
			"set_character_place_rulebook",
			char=self.name,
			rulebook=rb,
			branching=True,
		)
		self.engine._character_rulebooks_cache[self.name]["place"] = rb

	def _apply_delta(self, delta: NodeValDict) -> None:
		raise NotImplementedError("_apply_delta")

	@property
	def character(self) -> CharacterProxy:
		return self.engine.character[self.name]

	@property
	def _cache(self) -> StatDict:
		return self.engine._character_places_cache.setdefault(self.name, {})

	def __init__(self, engine_proxy: EngineProxy, character: CharName):
		self.engine: EngineProxy = engine_proxy
		self.name: CharName = character
		super().__init__()

	def __eq__(self, other):
		return self is other

	def _cache_set_munge(self, k: NodeName, v: StatDict) -> PlaceProxy:
		return PlaceProxy(self.character, k)

	def _set_item(self, k: NodeName, v: StatDict) -> None:
		self.engine.handle(
			command="set_place",
			char=self.name,
			place=k,
			statdict=v,
			branching=True,
		)
		self.engine._node_stat_cache[self.name][k] = v

	def _del_item(self, k: Stat) -> None:
		self.engine.handle(
			command="del_node", char=self.name, node=k, branching=True
		)
		del self.engine._node_stat_cache[self.name][k]

	def patch(self, d: NodeValDict) -> None:
		self._worker_check()
		things = d.keys() & self.character.thing.keys()
		if things:
			raise KeyError(f"Tried to patch things on place mapping: {things}")
		self.character.node.patch(d)


class SuccessorsProxy(CachingProxy):
	@property
	def _cache(self):
		succ = self.engine._character_portals_cache.successors
		return succ.setdefault(self._charname, {}).setdefault(self._orig, {})

	def _set_rulebook_name(self, k: RulebookName):
		raise NotImplementedError(
			"Set the rulebook on the .portal attribute, not this"
		)

	def __init__(
		self, engine_proxy: EngineProxy, charname: CharName, origname: NodeName
	):
		self.engine = engine_proxy
		self._charname = charname
		self._orig = origname
		super().__init__()

	def __eq__(self, other: SuccessorsProxy):
		return (
			isinstance(other, SuccessorsProxy)
			and self.engine is other.engine
			and self._charname == other._charname
			and self._orig == other._orig
		)

	def _apply_delta(self, delta):
		raise NotImplementedError(
			"Apply the delta on CharSuccessorsMappingProxy"
		)

	def _cache_set_munge(self, k: NodeName, v: PortalProxy | StatDict):
		if isinstance(v, PortalProxy):
			assert v._origin == self._orig
			assert v._destination == k
			return v
		return PortalProxy(
			self.engine.character[self._charname], self._orig, k
		)

	def _set_item(self, dest: NodeName, value: StatDict) -> None:
		self.engine.handle(
			command="set_portal",
			char=self._charname,
			orig=self._orig,
			dest=dest,
			statdict=value,
			branching=True,
		)

	def _del_item(self, dest: NodeName) -> None:
		self.engine.del_portal(self._charname, self._orig, dest)


class CharSuccessorsMappingProxy(CachingProxy, RuleFollowerProxy):
	def _get_default_rulebook_name(self) -> RulebookName:
		return "character_portal_rulebook", self.name

	def _get_rulebook_name(self) -> RulebookName:
		return self.engine._character_rulebooks_cache[self.name]["portal"]

	def _set_rulebook_name(self, rb: RulebookName) -> None:
		self.engine.handle(
			"set_character_portal_rulebook",
			char=self.character.name,
			rulebook=rb,
			branching=True,
		)
		self.engine._character_rulebooks_cache[self.name]["portal"] = rb

	@property
	def character(self) -> CharacterProxy:
		return self.engine.character[self.name]

	@property
	def _cache(self) -> dict[NodeName, dict[NodeName, PortalProxy]]:
		return self.engine._character_portals_cache.successors.setdefault(
			self.name, {}
		)

	def __init__(self, engine_proxy: EngineProxy, charname: CharName):
		self.engine: EngineProxy = engine_proxy
		self.name: CharName = charname
		super().__init__()

	def __eq__(self, other: CharSuccessorsMappingProxy):
		return (
			isinstance(other, CharSuccessorsMappingProxy)
			and other.engine is self.engine
			and other.name == self.name
		)

	def _cache_set_munge(self, k: None, v: dict[NodeName, NodeName]):
		return {
			vk: PortalProxy(self.character, vk, vv) for (vk, vv) in v.items()
		}

	def __contains__(self, k: NodeName):
		return k in self.character.node

	def __getitem__(self, k: NodeName) -> SuccessorsProxy:
		if k not in self.character.node:
			raise KeyError("No such node in this character", self.name, k)
		return SuccessorsProxy(self.engine, self.name, k)

	def _apply_delta(self, delta: EdgeValDict) -> None:
		for o, ds in delta.items():
			cache = self._cache[o]
			for d, stats in ds.items():
				if d not in cache:
					cache[d] = PortalProxy(self.character, o, d)
				cache[d]._apply_delta(stats)

	def _set_item(self, orig: NodeName, val: dict[NodeName, StatDict]) -> None:
		self.engine.handle(
			command="character_set_node_successors",
			character=self.name,
			node=orig,
			val=val,
			branching=True,
		)

	def _del_item(self, orig: NodeName) -> None:
		for dest in self[orig]:
			self.engine.del_portal(self.name, orig, dest)


class PredecessorsProxy(MutableMapping):
	@property
	def character(self) -> CharacterProxy:
		return self.engine.character[self._charname]

	def _worker_check(self):
		self.engine._worker_check()

	def __init__(
		self, engine_proxy: EngineProxy, charname: CharName, destname: NodeName
	):
		self.engine: EngineProxy = engine_proxy
		self._charname: CharName = charname
		self.name: NodeName = destname

	def __iter__(self) -> Iterator[NodeName]:
		preds = self.engine._character_portals_cache.predecessors
		if (
			self._charname not in preds
			or self.name not in preds[self._charname]
		):
			return iter(())
		return iter(preds[self._charname][self.name])

	def __len__(self):
		preds = self.engine._character_portals_cache.predecessors
		if (
			self._charname not in preds
			or self.name not in preds[self._charname]
		):
			return 0
		return len(preds[self._charname][self.name])

	def __contains__(self, k: NodeName):
		preds = self.engine._character_portals_cache.predecessors
		return (
			self._charname in preds
			and self.name in preds[self._charname]
			and k in preds[self._charname][self.name]
		)

	def __getitem__(self, k: NodeName):
		return self.engine._character_portals_cache.predecessors[
			self._charname
		][self.name][k]

	def __setitem__(self, k: NodeName, v: dict[NodeName, StatDict]):
		self._worker_check()
		self.engine._character_portals_cache.store(
			self._charname,
			self.name,
			k,
			PortalProxy(self.engine.character[self._charname], k, self.name),
		)
		self.engine.handle(
			command="set_place",
			char=self._charname,
			place=k,
			statdict=v,
			branching=True,
		)
		self.engine.handle(
			"set_portal",
			char=self._charname,
			orig=self.name,
			dest=k,
			value=v,
			branching=True,
		)

	def __delitem__(self, k: NodeName) -> None:
		self.engine.del_portal(self._charname, k, self.name)


class CharPredecessorsMappingProxy(MutableMapping, Signal):
	@property
	def _cache(self) -> dict[NodeName, dict[NodeName, PortalProxy]]:
		return self.engine._character_portals_cache.predecessors.setdefault(
			self.name, {}
		)

	def _worker_check(self) -> None:
		self.engine._worker_check()

	def __init__(self, engine_proxy: EngineProxy, charname: CharName):
		super().__init__()
		self.engine: EngineProxy = engine_proxy
		self.name: CharName = charname
		self._obj_cache = {}

	def __contains__(self, k: NodeName):
		return k in self.engine.character[self.name].node

	def __iter__(self) -> Iterator[NodeName]:
		try:
			return iter(
				self.engine._character_portals_cache.predecessors[self.name]
			)
		except KeyError:
			return iter(())

	def __len__(self):
		try:
			return len(
				self.engine._character_portals_cache.predecessors[self.name]
			)
		except KeyError:
			return 0

	def __getitem__(self, k: NodeName) -> PredecessorsProxy:
		if k not in self:
			raise KeyError("No such node in this character", self.name, k)
		if k not in self._obj_cache:
			self._obj_cache[k] = PredecessorsProxy(self.engine, self.name, k)
		return self._obj_cache[k]

	def __setitem__(self, k: NodeName, v: dict[NodeName, PortalProxy]):
		self._worker_check()
		for pred, proxy in v.items():
			self.engine._character_portals_cache.store(
				self.name, pred, k, proxy
			)
		self.engine.handle(
			command="character_set_node_predecessors",
			char=self.name,
			node=k,
			preds=v,
			branching=True,
		)

	def __delitem__(self, k: NodeName):
		self._worker_check()
		for v in list(self[k]):
			self.engine.del_portal(self.name, v, k)


class CharStatProxy(CachingEntityProxy):
	@property
	def _cache(self):
		return self.engine._char_stat_cache[self.name]

	def __init__(self, character: CharacterProxy):
		self.engine = character.engine
		self.name = character.name
		super().__init__()

	def __eq__(self, other: dict):
		if not hasattr(other, "keys") or not callable(other.keys):
			return False
		if self.keys() != other.keys():
			return False
		for k, v in self.items():
			if hasattr(v, "unwrap"):
				v = v.unwrap()
			if v != other[k]:
				return False
		return True

	def unwrap(self):
		return dict(self)

	def _set_rulebook_name(self, k: RulebookName):
		raise NotImplementedError(
			"Set rulebooks on the Character proxy, not this"
		)

	def _get(self, k: Optional[Key] = None):
		if k is None:
			return self
		return self._cache[k]

	def _set_item(self, k: Key, v: Value):
		if k == "name":
			raise KeyError("Can't change names")
		self.engine.handle(
			command="set_character_stat",
			char=self.name,
			k=k,
			v=v,
			branching=True,
		)

	def _del_item(self, k: Key):
		self.engine.handle(
			command="del_character_stat", char=self.name, k=k, branching=True
		)

	def _apply_delta(self, delta: StatDict):
		for k, v in delta.items():
			assert k != "rulebook"
			if v is ...:
				if k in self._cache:
					del self._cache[k]
					self.send(self, key=k, value=...)
			elif k not in self._cache or self._cache[k] != v:
				self._cache[k] = v
				self.send(self, key=k, value=v)


class FuncListProxy(MutableSequence, Signal):
	def __init__(
		self,
		rule_proxy: RuleProxy,
		key: Literal["triggers", "prereqs", "actions"],
	):
		super().__init__()
		self.rule = rule_proxy
		self._key = key

	def __iter__(self):
		return iter(self.rule._cache.get(self._key, ()))

	def __len__(self):
		return len(self.rule._cache.get(self._key, ()))

	def __getitem__(self, item: int):
		if self._key not in self.rule._cache:
			raise IndexError(item)
		return self.rule._cache[self._key][item]

	def index(
		self,
		value: FuncName | FuncProxy,
		start: int = 0,
		stop: int | ... = ...,
	):
		if not isinstance(value, FuncProxy):
			value = getattr(self._get_store(), value)
		kwargs = {"start": start}
		if stop is not ...:
			kwargs["stop"] = stop
		return super().index(value, **kwargs)

	def _handle_send(self):
		self.rule.engine.handle(
			f"set_rule_{self._key}",
			**{
				"rule": self.rule.name,
				"branching": True,
				self._key: self.rule._nominate(self.rule._cache[self._key]),
			},
		)

	def _get_store(self) -> FuncStoreProxy:
		return getattr(self.rule.engine, self._key[:-1])

	def __setitem__(self, i: int, value: FuncName | FuncProxy):
		if isinstance(value, str):
			value = getattr(self._get_store(), value)
		if self._key in self.rule._cache:
			self.rule._cache[self._key][i] = value
		elif i == 0:
			self.rule._cache[self._key] = [value]
		else:
			raise IndexError(i)
		self._handle_send()

	def __delitem__(self, key: int):
		if self._key not in self.rule._cache:
			raise IndexError(key)
		del self.rule._cache[self._key][key]
		self._handle_send()

	def insert(self, index: int, value: FuncProxy | FuncName):
		if isinstance(value, str):
			value = getattr(self._get_store(), value)
		elif not isinstance(value, FuncProxy):
			setattr(self._get_store(), value.__name__, value)
			value = getattr(self._get_store(), value.__name__)
		self.rule._cache.setdefault(self._key, []).insert(index, value)
		self._handle_send()


class FuncListProxyDescriptor:
	def __init__(self, key):
		self._key = key

	def __get__(self, instance, owner):
		attname = f"_{self._key}_proxy"
		if not hasattr(instance, attname):
			setattr(instance, attname, FuncListProxy(instance, self._key))
		return getattr(instance, attname)

	def __set__(self, instance, value):
		to_set = []
		for v in value:
			if isinstance(v, FuncProxy):
				to_set.append(v)
			elif not isinstance(v, str):
				raise TypeError(f"Need FuncListProxy or str, got {type(v)}")
			else:
				to_set.append(
					getattr(
						getattr(instance.engine, self._key.removesuffix("s")),
						v,
					)
				)
		instance._cache[self._key] = to_set
		self.__get__(instance, None)._handle_send()


class RuleProxy(Signal):
	triggers = FuncListProxyDescriptor("triggers")
	prereqs = FuncListProxyDescriptor("prereqs")
	actions = FuncListProxyDescriptor("actions")

	@staticmethod
	def _nominate(v):
		ret = []
		for whatever in v:
			if hasattr(whatever, "name"):
				ret.append(whatever.name)
			elif hasattr(whatever, "__name__"):
				ret.append(whatever.__name__)
			else:
				assert isinstance(whatever, str), whatever
				ret.append(whatever)
		return ret

	@property
	def _cache(self):
		return self.engine._rules_cache.setdefault(self.name, {})

	@property
	def neighborhood(self) -> RuleNeighborhood:
		if self.name not in self.engine._neighborhood_cache:
			return self.engine._neighborhood_cache.setdefault(
				self.name,
				self.engine.handle("get_rule_neighborhood", rule=self.name),
			)
		return self.engine._neighborhood_cache[self.name]

	@neighborhood.setter
	def neighborhood(self, v: RuleNeighborhood):
		self.engine._worker_check()
		self.engine.handle(
			"set_rule_neighborhood", rule=self.name, neighborhood=v
		)
		self.engine._neighborhood_cache[self.name] = v

	def trigger(self, trigger: callable | FuncProxy) -> FuncProxy:
		self.triggers.append(trigger)
		if isinstance(trigger, FuncProxy):
			return trigger
		else:
			return getattr(self.engine.trigger, trigger.__name__)

	def prereq(self, prereq: callable | FuncProxy) -> FuncProxy:
		self.prereqs.append(prereq)
		if isinstance(prereq, FuncProxy):
			return prereq
		else:
			return getattr(self.engine.prereq, prereq.__name__)

	def action(self, action: callable | FuncProxy) -> FuncProxy:
		self.actions.append(action)
		if isinstance(action, FuncProxy):
			return action
		else:
			return getattr(self.engine.action, action.__name__)

	def __init__(self, engine: EngineProxy, rulename: RuleName):
		super().__init__()
		self.engine = engine
		self.name = self._name = rulename
		if rulename not in engine._rules_cache:
			engine.handle("new_empty_rule", rule=rulename)
			engine._rules_cache[rulename] = {}

	def __eq__(self, other):
		return hasattr(other, "name") and self.name == other.name


class RuleBookProxy(MutableSequence, Signal):
	@property
	def _cache(
		self,
	) -> list[RuleName]:
		no_rules: list[RuleName] = []
		zero_prio = RulebookPriority(0.0)
		return self.engine._rulebooks_cache.setdefault(
			self.name, (no_rules, zero_prio)
		)[0]

	@property
	def priority(self) -> RulebookPriority:
		no_rules: list[RuleName] = []
		zero_prio = RulebookPriority(0.0)
		return self.engine._rulebooks_cache.setdefault(
			self.name, (no_rules, zero_prio)
		)[1]

	def _worker_check(self):
		self.engine._worker_check()

	def __init__(self, engine: EngineProxy, bookname: RulebookName):
		super().__init__()
		self.engine = engine
		self.name = bookname
		self._proxy_cache = engine._rule_obj_cache

	def __iter__(self) -> Iterator[RulebookName]:
		for k in self._cache:
			if k not in self._proxy_cache:
				self._proxy_cache[k] = RuleProxy(self.engine, k)
			yield self._proxy_cache[k]

	def __len__(self):
		return len(self._cache)

	def __getitem__(self, i):
		k = self._cache[i]
		if k not in self._proxy_cache:
			self._proxy_cache[k] = RuleProxy(self.engine, k)
		return self._proxy_cache[k]

	def __setitem__(self, i, v: RuleProxy | RuleName):
		self._worker_check()
		if isinstance(v, RuleProxy):
			v = v._name
		self._cache[i] = v
		self.engine.handle(
			command="set_rulebook_rule",
			rulebook=self.name,
			i=i,
			rule=v,
			branching=True,
		)
		self.send(self, i=i, val=v)

	def __delitem__(self, i):
		self._worker_check()
		del self._cache[i]
		self.engine.handle(
			command="del_rulebook_rule",
			rulebook=self.name,
			i=i,
			branching=True,
		)
		self.send(self, i=i, val=None)

	def insert(self, i: int, v: RuleProxy | RuleName):
		self._worker_check()
		if isinstance(v, RuleProxy):
			v = v._name
		self._cache.insert(i, v)
		self.engine.handle(
			command="ins_rulebook_rule",
			rulebook=self.name,
			i=i,
			rule=v,
			branching=True,
		)
		for j in range(i, len(self)):
			self.send(self, i=j, val=self[j])

	def move_rule_back(self, i: int) -> int:
		self._worker_check()
		if i <= 0 or i > len(self):
			raise IndexError("Invalid rule index", i)
		prox = self._cache.pop(i)
		self._cache.insert(i - 1, prox)
		return self.engine.handle(
			"move_rulebook_rule_back",
			rulebook=self.name,
			i=i,
			cb=partial(self.send, self, i=i - 1, val=prox),
		)

	def move_rule_forward(self, i: int):
		self._worker_check()
		if i < 0 or i >= len(self):
			raise IndexError("Invalid rule index", i)
		prox = self._cache.pop(i)
		self._cache.insert(i + 1, prox)
		return self.engine.handle(
			"move_rulebook_rule_forward",
			rulebook=self.name,
			i=i,
			cb=partial(self.send, self, i=i + 1, val=prox),
		)


class UnitMapProxy(Mapping, RuleFollowerProxy, Signal):
	engine = getatt("character.engine")

	def _get_default_rulebook_name(self) -> RulebookName:
		return RulebookName(Key(("unit_rulebook", self.character.name)))

	def _get_rulebook_name(self) -> RulebookName:
		return self.engine._character_rulebooks_cache[self.character.name][
			"unit"
		]

	def _set_rulebook_name(self, rb: RulebookName) -> None:
		self.engine.handle(
			"set_unit_rulebook",
			char=self.character.name,
			rulebook=rb,
			branching=True,
		)
		self.engine._character_rulebooks_cache[self.character.name]["unit"] = (
			rb
		)

	@property
	def only(self) -> NodeProxy:
		if len(self) == 0:
			raise AttributeError("No units")
		elif len(self) > 1:
			raise AttributeError("Units in more than one graph")
		return next(iter(self.values()))

	def __init__(self, character: CharacterProxy):
		super().__init__()
		self.character = character

	def __iter__(self) -> Iterator[NodeProxy]:
		yield from self.character.engine._character_units_cache[
			self.character.name
		]

	def __len__(self):
		return len(
			self.character.engine._character_units_cache[self.character.name]
		)

	def __contains__(self, k: CharName):
		return (
			k
			in self.character.engine._character_units_cache[
				self.character.name
			]
		)

	def __getitem__(self, k: CharName) -> GraphUnitsProxy:
		if k not in self:
			raise KeyError(
				"{} has no unit in {}".format(self.character.name, k)
			)
		return self.GraphUnitsProxy(
			self.character, self.character.engine.character[k]
		)

	class GraphUnitsProxy(Mapping):
		def __init__(self, character: CharacterProxy, graph: CharacterProxy):
			self.character = character
			self.graph = graph

		def __iter__(self):
			yield from self.character.engine._character_units_cache[
				self.character.name
			][self.graph.name]

		def __len__(self):
			return len(
				self.character.engine._character_units_cache[
					self.character.name
				][self.graph.name]
			)

		def __contains__(self, k: NodeName):
			cache = self.character.engine._character_units_cache[
				self.character.name
			]
			return self.graph.name in cache and k in cache[self.graph.name]

		def __getitem__(self, k: NodeName):
			if k not in self:
				raise KeyError(
					"{} has no unit {} in graph {}".format(
						self.character.name, k, self.graph.name
					)
				)
			return self.graph.node[k]

		@property
		def only(self) -> NodeProxy:
			if len(self) != 1:
				raise AttributeError("No unit, or more than one")
			return next(iter(self.values()))


class CharacterProxy(AbstractCharacter, RuleFollowerProxy):
	adj_cls = CharSuccessorsMappingProxy
	pred_cls = CharPredecessorsMappingProxy
	graph_map_cls = CharStatProxy

	def copy_from(self, g: AbstractCharacter) -> None:
		self._worker_check()
		# can't handle multigraphs
		self.engine.handle(
			"character_copy_from",
			char=self.name,
			nodes=g._node,
			adj=g._adj,
			branching=True,
		)
		for node, nodeval in g.nodes.items():
			if node not in self.node:
				if nodeval and "location" in nodeval:
					self.thing._cache[node] = ThingProxy(
						self, node, nodeval["location"]
					)
				else:
					self.place._cache[node] = PlaceProxy(self, node)
		for orig in g.adj:
			for dest, edge in g.adj[orig].items():
				if orig in self.portal and dest in self.portal[orig]:
					self.portal[orig][dest]._apply_delta(edge)
				else:
					self.portal._cache[orig][dest] = PortalProxy(
						self, orig, dest
					)
					self.engine._portal_stat_cache[self.name][orig][dest] = (
						edge
					)

	def _get_default_rulebook_name(self) -> RulebookName:
		return RulebookName(Key(("character_rulebook", self.name)))

	def _get_rulebook_name(self) -> RulebookName:
		return self.engine._character_rulebooks_cache[self.name]["character"]

	def _set_rulebook_name(self, rb: RulebookName) -> None:
		self.engine.handle(
			"set_character_rulebook",
			char=self.name,
			rulebook=rb,
			branching=True,
		)
		self.engine._character_rulebooks_cache[self.name]["character"] = rb

	@cached_property
	def unit(self) -> UnitMapProxy:
		return UnitMapProxy(self)

	@staticmethod
	def PortalSuccessorsMapping(self) -> CharSuccessorsMappingProxy:
		return CharSuccessorsMappingProxy(self.engine, self.name)

	@staticmethod
	def PortalPredecessorsMapping(self) -> CharPredecessorsMappingProxy:
		return CharPredecessorsMappingProxy(self.engine, self.name)

	@staticmethod
	def ThingMapping(self) -> ThingMapProxy:
		return ThingMapProxy(self.engine, self.name)

	@staticmethod
	def PlaceMapping(self) -> PlaceMapProxy:
		return PlaceMapProxy(self.engine, self.name)

	@staticmethod
	def ThingPlaceMapping(self) -> NodeMapProxy:
		return NodeMapProxy(self.engine, self.name)

	def __init__(
		self,
		engine_proxy: EngineProxy,
		charname: CharName,
		*,
		init_rulebooks: bool = False,
	):
		assert not init_rulebooks, (
			"Can't initialize rulebooks in CharacterProxy"
		)
		self.db: EngineProxy = engine_proxy
		self._name: CharName = charname

	def __repr__(self):
		return f"{self.db}.character[{repr(self.name)}]"

	def __bool__(self):
		return self._name in self.db.character

	def __eq__(self, other):
		if hasattr(other, "engine"):
			return (
				self.engine is other.engine
				and hasattr(other, "name")
				and self.name == other.name
			)
		else:
			return False

	def _apply_delta(self, delta: CharDelta):
		delta = delta.copy()
		deleted_nodes = set()
		for node, ex in delta.pop("nodes", {}).items():
			if ex:
				if node not in self.node:
					nodeval = delta.get("node_val", {}).get(node, ...)
					if nodeval is not ... and "location" in nodeval:
						self.thing._cache[node] = prox = ThingProxy(
							self, node, NodeName(Key(nodeval["location"]))
						)
						self.thing.send(prox, key=None, value=True)
					else:
						self.place._cache[node] = prox = PlaceProxy(self, node)
						self.place.send(prox, key=None, value=True)
					self.node.send(prox, key=None, value=True)
			elif node in self.node:
				deleted_nodes.add(node)
				prox = self.node[node]
				if node in self.place._cache:
					del self.place._cache[node]
					self.place.send(prox, key=None, value=False)
				elif node in self.thing._cache:
					del self.thing._cache[node]
					self.thing.send(prox, key=None, value=False)
				else:
					self.engine.warning(
						"Diff deleted {} but it was never created here".format(
							node
						)
					)
				self.node.send(prox, key=None, value=False)
			else:
				deleted_nodes.add(node)
		for orig, dests in delta.pop("edges", {}).items():
			for dest, ex in dests.items():
				if ex:
					self.engine._character_portals_cache.store(
						self.name, orig, dest, PortalProxy(self, orig, dest)
					)
					self.portal.send(
						self.portal[orig][dest], key=None, value=True
					)
				elif orig in self.portal and dest in self.portal[orig]:
					prox = self.portal[orig][dest]
					try:
						self.engine._character_portals_cache.delete(
							self.name, orig, dest
						)
						assert dest not in self.portal[orig]
					except KeyError:
						pass
					self.portal.send(prox, key=None, value=False)
		self.portal._apply_delta(delta.pop("edge_val", {}))
		nodemap = self.node
		name = self.name
		engine = self.engine
		node_stat_cache = engine._node_stat_cache
		nodedelts: NodeValDict = delta.pop("node_val", {})
		for node, nodedelta in nodedelts.items():
			if node in deleted_nodes:
				continue
			elif node not in node_stat_cache[name]:
				rulebook = nodedelta.pop("rulebook", None)
				node_stat_cache[name][node] = nodedelta
				if rulebook:
					nodemap[node]._set_rulebook_name(rulebook)
			else:
				nodemap[node]._apply_delta(nodedelta)
		portmap = self.portal
		portal_stat_cache = self.engine._portal_stat_cache
		portdelts: EdgeValDict = delta.pop("edge_val", {})
		for orig, destdelta in portdelts.items():
			if orig in portmap:
				destmap = portmap[orig]
				for dest, portdelta in destdelta.items():
					if dest in destmap:
						destmap[dest]._apply_delta(portdelta)
			else:
				porig = portal_stat_cache[name][orig]
				for dest, portdelta in destdelta.items():
					rulebook = portdelta.pop("rulebook", None)
					porig[dest] = portdelta
					if rulebook:
						self.engine._char_port_rulebooks_cache[name][orig][
							dest
						] = rulebook
		ruc = self.engine._character_rulebooks_cache[name]
		if "character_rulebook" in delta:
			ruc["character"] = delta.pop("character_rulebook")
		if "unit_rulebook" in delta:
			ruc["unit"] = delta.pop("unit_rulebook")
		if "character_thing_rulebook" in delta:
			ruc["thing"] = delta.pop("character_thing_rulebook")
		if "character_place_rulebook" in delta:
			ruc["place"] = delta.pop("character_place_rulebook")
		if "character_portal_rulebook" in delta:
			ruc["portal"] = delta.pop("character_portal_rulebook")
		self.stat._apply_delta(delta)

	def add_place(self, name: NodeName, **kwargs: StatDict) -> None:
		self._worker_check()
		self.engine.handle(
			command="set_place",
			char=self.name,
			place=name,
			statdict=kwargs,
			branching=True,
		)
		self.place._cache[name] = PlaceProxy(self, name)
		self.engine._node_stat_cache[self.name][name] = kwargs

	def add_places_from(self, seq: Iterable[NodeName]):
		self._worker_check()
		self.engine.handle(
			command="add_places_from",
			char=self.name,
			seq=list(seq),
			branching=True,
		)
		placecache = self.place._cache
		nodestatcache = self.engine._node_stat_cache[self.name]
		for pln in seq:
			if isinstance(pln, tuple):
				placecache[pln[0]] = PlaceProxy(self, *pln)
				if len(pln) > 1:
					nodestatcache[pln[0]] = pln[1]
			else:
				placecache[pln] = PlaceProxy(self, pln)

	def add_nodes_from(self, seq: Iterable[NodeName], **attrs):
		self._worker_check()
		self.add_places_from(seq)

	def add_thing(
		self, name: NodeName, location: NodeName, **kwargs: StatDict
	) -> None:
		self._worker_check()
		self.engine.handle(
			command="add_thing",
			char=self.name,
			thing=name,
			loc=location,
			statdict=kwargs,
			branching=True,
		)
		self.thing._cache[name] = thing = ThingProxy(
			self, name, location, **kwargs
		)
		self.thing.send(thing, key=None, value=True)
		self.node.send(thing, key=None, value=True)

	def _worker_check(self):
		self.engine._worker_check()

	def add_things_from(self, seq: Iterable[NodeName], **attrs) -> None:
		self._worker_check()
		self.engine.handle(
			command="add_things_from",
			char=self.name,
			seq=list(seq),
			branching=True,
		)
		for name, location in seq:
			self.thing._cache[name] = thing = ThingProxy(self, name, location)
			self.thing.send(thing, key=None, value=True)
			self.node.send(thing, key=None, value=True)

	def place2thing(self, place: NodeName, location: NodeName) -> None:
		self._worker_check()
		self.engine.handle(
			command="place2thing",
			char=self.name,
			place=place,
			loc=location,
			branching=True,
		)
		if place in self.place._cache:
			del self.place._cache[place]
		self.place.send(place, key=None, value=False)
		if place not in self.thing._cache:
			self.thing._cache[place] = ThingProxy(self, place, location)
		self.thing.send(place, key=None, value=True)

	def thing2place(self, thing: NodeName) -> None:
		self._worker_check()
		self.engine.handle(
			command="thing2place",
			char=self.name,
			thing=thing,
			branching=True,
		)
		if thing in self.thing._cache:
			del self.thing._cache[thing]
		self.thing.send(thing, key=None, value=False)
		if thing not in self.place._cache:
			self.place._cache[thing] = PlaceProxy(self, thing)
		self.place.send(thing, key=None, value=True)

	def remove_node(self, node: NodeName) -> None:
		self._worker_check()
		if node not in self.node:
			raise KeyError("No such node: {}".format(node))
		name = self.name
		self.engine.handle("del_node", char=name, node=node, branching=True)
		placecache = self.place._cache
		thingcache = self.thing._cache
		if node in placecache:
			it = placecache[node]
			it.send(it, key=None, value=False)
			self.place.send(it, key=None, value=False)
			del placecache[node]
		else:
			it = thingcache[node]
			it.send(it, key=None, value=False)
			self.thing.send(it, key=None, value=False)
			del thingcache[node]
		self.node.send(it, key=None, value=False)
		portscache = self.engine._character_portals_cache
		to_del = set()
		if (
			name in portscache.successors
			and node in portscache.successors[name]
		):
			to_del.update(
				(node, dest) for dest in portscache.successors[name][node]
			)
		if (
			name in portscache.predecessors
			and node in portscache.predecessors[name]
		):
			to_del.update(
				(orig, node) for orig in portscache.predecessors[name][node]
			)
		for u, v in to_del:
			portscache.delete(name, u, v)
		if (
			name in portscache.successors
			and node in portscache.successors[name]
		):
			del portscache.successors[name][node]
		if name in portscache.successors and not portscache.successors[name]:
			del portscache.successors[name]
		if (
			name in portscache.predecessors
			and node in portscache.predecessors[name]
		):
			del portscache.predecessors[name][node]
		if (
			name in portscache.predecessors
			and not portscache.predecessors[name]
		):
			del portscache.predecessors[name]

	def remove_place(self, place: NodeName) -> None:
		self._worker_check()
		placemap = self.place
		if place not in placemap:
			raise KeyError("No such place: {}".format(place))
		name = self.name
		self.engine.handle("del_node", char=name, node=place, branching=True)
		del placemap._cache[place]
		portscache = self.engine._character_portals_cache
		del portscache.successors[name][place]
		del portscache.predecessors[name][place]

	def remove_thing(self, thing: NodeName) -> None:
		self._worker_check()
		thingmap = self.thing
		if thing not in thingmap:
			raise KeyError("No such thing: {}".format(thing))
		name = self.name
		self.engine.handle("del_node", char=name, node=thing, branching=True)
		del thingmap._cache[thing]
		portscache = self.engine._character_portals_cache
		del portscache.successors[name][thing]
		del portscache.predecessors[name][thing]

	def add_portal(
		self, origin: NodeName, destination: NodeName, **kwargs: StatDict
	) -> None:
		self._worker_check()
		symmetrical = kwargs.pop("symmetrical", False)
		origin = getattr(origin, "name", origin)
		destination = getattr(destination, "name", destination)
		self.engine.handle(
			command="add_portal",
			char=self.name,
			orig=origin,
			dest=destination,
			symmetrical=symmetrical,
			statdict=kwargs,
			branching=True,
		)
		self.engine._character_portals_cache.store(
			self.name,
			origin,
			destination,
			PortalProxy(self, origin, destination),
		)
		if symmetrical:
			self.engine._character_portals_cache.store(
				self.name,
				destination,
				origin,
				PortalProxy(self, destination, origin),
			)
		node = self._node
		placecache = self.place._cache

		if origin not in node:
			placecache[origin] = PlaceProxy(self, origin)
		if destination not in node:
			placecache[destination] = PlaceProxy(self, destination)

	def remove_portal(self, origin: NodeName, destination: NodeName) -> None:
		self._worker_check()
		char_port_cache = self.engine._character_portals_cache
		cache = char_port_cache.successors[self.name]
		if origin not in cache or destination not in cache[origin]:
			raise KeyError(
				"No portal from {} to {}".format(origin, destination)
			)
		self.engine.handle(
			"del_portal",
			char=self.name,
			orig=origin,
			dest=destination,
			branching=True,
		)
		char_port_cache.delete(self.name, origin, destination)

	remove_edge = remove_portal

	def add_portals_from(
		self, seq: Iterable[tuple[NodeName, NodeName]], symmetrical=False
	):
		self._worker_check()
		l = list(seq)
		self.engine.handle(
			command="add_portals_from",
			char=self.name,
			seq=l,
			symmetrical=symmetrical,
			branching=True,
		)
		for origin, destination in l:
			if origin not in self.portal._cache:
				self.portal._cache[origin] = SuccessorsProxy(
					self.engine, self.name, origin
				)
			self.portal[origin]._cache[destination] = PortalProxy(
				self, origin, destination
			)

	def portals(self) -> Iterator[PortalProxy]:
		for ds in self.portal.values():
			yield from ds.values()

	def add_unit(
		self, graph: CharName | CharacterProxy, node: Optional[NodeName] = None
	) -> None:
		self._worker_check()
		# TODO: cache
		if node is None:
			node = graph.name
			graph = graph.character.name
		self.engine._character_units_cache[self.name].setdefault(
			graph, set()
		).add(node)
		self.engine._unit_characters_cache[graph].setdefault(node, set()).add(
			self.name
		)
		self.engine.handle(
			command="add_unit",
			char=self.name,
			graph=graph,
			node=node,
			branching=True,
		)

	def remove_unit(
		self, graph: CharName | CharacterProxy, node: Optional[NodeName] = None
	) -> None:
		self._worker_check()
		# TODO: cache
		if node is None:
			node = graph.name
			graph = graph.character.name
		self.engine.handle(
			command="remove_unit",
			char=self.name,
			graph=graph,
			node=node,
			branching=True,
		)

	def units(self) -> Iterator[NodeProxy]:
		yield from self.engine.handle(
			command="character_units", char=self.name
		)

	def facade(self) -> CharacterFacade:
		return CharacterFacade(character=self)

	def grid_2d_8graph(self, m: int, n: int) -> None:
		self.engine.handle(
			"grid_2d_8graph",
			character=self.name,
			m=m,
			n=n,
			cb=self.engine._upd_caches,
		)

	def grid_2d_graph(self, m: int, n: int, periodic: bool = False) -> None:
		self.engine.handle(
			"grid_2d_graph",
			character=self.name,
			m=m,
			n=n,
			periodic=periodic,
			cb=self.engine._upd_caches,
		)


class CharacterMapProxy(MutableMapping, Signal):
	def _worker_check(self):
		self.engine._worker_check()

	def __init__(self, engine_proxy: EngineProxy):
		super().__init__()
		self.engine = engine_proxy

	def __iter__(self) -> Iterator[CharName]:
		return iter(self.engine._char_cache.keys())

	def __contains__(self, k: CharName):
		return k in self.engine._char_cache

	def __len__(self):
		return len(self.engine._char_cache)

	def __getitem__(self, k: CharName) -> CharacterProxy:
		return self.engine._char_cache[k]

	def __setitem__(self, k: CharName, v: CharDelta):
		self._worker_check()
		self.engine.handle(
			command="set_character", char=k, data=v, branching=True
		)
		self.engine._char_cache[k] = CharacterProxy(self.engine, k)
		self.send(self, key=k, val=v)

	def __delitem__(self, k: CharName):
		self._worker_check()
		self.engine.handle(command="del_character", char=k, branching=True)
		for graph, characters in self.engine._unit_characters_cache.items():
			if k in characters:
				del characters[k]
		successors = self.engine._character_portals_cache.successors
		predecessors = self.engine._character_portals_cache.predecessors
		if k in successors:
			del successors[k]
		if k in predecessors:
			del predecessors[k]
		for cache_name in (
			"_char_cache",
			"_node_stat_cache",
			"_portal_stat_cache",
			"_char_stat_cache",
			"_things_cache",
			"_character_places_cache",
			"_character_rulebooks_cache",
			"_char_node_rulebooks_cache",
			"_char_port_rulebooks_cache",
			"_character_units_cache",
		):
			cache = getattr(self.engine, cache_name)
			if k in cache:
				del cache[k]
		self.send(self, key=k, val=None)


class ProxyLanguageDescriptor(AbstractLanguageDescriptor):
	def _get_language(self, inst):
		if not hasattr(inst, "_language"):
			inst._language = inst.engine.handle(command="get_language")
		return inst._language

	def _set_language(self, inst, val):
		inst._language = val
		delta = inst.engine.handle(command="set_language", lang=val)
		cache = inst._cache
		for k, v in delta.items():
			if k in cache:
				if v is None:
					del cache[k]
				elif cache[k] != v:
					cache[k] = v
					inst.send(inst, key=k, string=v)
			elif v is not None:
				cache[k] = v
				inst.send(inst, key=k, string=v)


class StringStoreProxy(Signal):
	language = ProxyLanguageDescriptor()
	_cache: dict
	_store = "string"

	def __init__(self, engine_proxy: EngineProxy):
		self._cache = {}
		super().__init__()
		self.engine = engine_proxy

	def _worker_check(self):
		self.engine._worker_check()

	def load(self) -> None:
		self._cache = self.engine.handle("strings_copy")

	def __getattr__(self, k: str) -> str:
		cache = super().__getattribute__("_cache")
		if k in cache:
			return cache[k]
		raise AttributeError(k)

	def __setattr__(self, k: str, v: str):
		if k in (
			"_cache",
			"engine",
			"language",
			"_language",
			"receivers",
			"_by_receiver",
			"_by_sender",
			"_weak_senders",
			"is_muted",
		):
			super().__setattr__(k, v)
			return
		self._worker_check()
		self._cache[k] = v
		self.engine.handle(command="set_string", k=k, v=v)
		self.send(self, key=k, string=v)

	def __delattr__(self, k: str):
		self._worker_check()
		del self._cache[k]
		self.engine.handle(command="del_string", k=k)
		self.send(self, key=k, string=None)

	def lang_items(self, lang: Optional[str] = None):
		if lang is None or lang == self.language:
			yield from self._cache.items()
		else:
			yield from self.engine.handle(
				command="get_string_lang_items", lang=lang
			)


class EternalVarProxy(MutableMapping):
	@property
	def _cache(self):
		return self.engine._eternal_cache

	def _worker_check(self):
		self.engine._worker_check()

	def __init__(self, engine_proxy):
		self.engine = engine_proxy

	def __contains__(self, k: EternalKey):
		return k in self._cache

	def __iter__(self):
		return iter(self._cache)

	def __len__(self):
		return len(self._cache)

	def __getitem__(self, k: EternalKey):
		return self._cache[k]

	def __setitem__(self, k: EternalKey, v: Value):
		self._worker_check()
		self._cache[k] = v
		self.engine.handle("set_eternal", k=k, v=v)

	def __delitem__(self, k: EternalKey):
		self._worker_check()
		del self._cache[k]
		self.engine.handle(command="del_eternal", k=k)

	def _update_cache(self, data: dict[EternalKey, Value]):
		for k, v in data.items():
			if v is None:
				del self._cache[k]
			else:
				self._cache[k] = v


class GlobalVarProxy(MutableMapping, Signal):
	@property
	def _cache(self):
		return self.engine._universal_cache

	def _worker_check(self):
		self.engine._worker_check()

	def __init__(self, engine_proxy: EngineProxy):
		super().__init__()
		self.engine = engine_proxy

	def __iter__(self):
		return iter(self._cache)

	def __len__(self):
		return len(self._cache)

	def __getitem__(self, k: UniversalKey):
		return self._cache[k]

	def __setitem__(self, k: UniversalKey, v: Value):
		self._worker_check()
		self._cache[k] = v
		self.engine.handle("set_universal", k=k, v=v, branching=True)
		self.send(self, key=k, value=v)

	def __delitem__(self, k: UniversalKey):
		self._worker_check()
		del self._cache[k]
		self.engine.handle("del_universal", k=k, branching=True)
		self.send(self, key=k, value=None)

	def _update_cache(self, data: dict[UniversalKey, Value]):
		for k, v in data.items():
			if v is None:
				if k not in self._cache:
					continue
				del self._cache[k]
				self.send(self, key=k, value=None)
			else:
				self._cache[k] = v
				self.send(self, key=k, value=v)


class AllRuleBooksProxy(MutableMapping):
	@property
	def _cache(self):
		return self.engine._rulebooks_cache

	def __init__(self, engine_proxy):
		self.engine = engine_proxy
		self._objs: dict[RulebookName, RuleBookProxy] = {}

	def __iter__(self):
		yield from self._cache

	def __len__(self):
		return len(self._cache)

	def __contains__(self, k: RulebookName):
		return k in self._cache

	def __getitem__(self, k: RulebookName):
		if k not in self:
			self.engine.handle("new_empty_rulebook", rulebook=k)
			no_rules: list[RuleName] = []
			zero_prio = RulebookPriority(0.0)
			self._cache[k] = no_rules, zero_prio
		if k not in self._objs:
			self._objs[k] = RuleBookProxy(self.engine, k)
		return self._objs[k]

	def __setitem__(
		self,
		key: RulebookName,
		value: FuncListProxy | Iterable[RuleProxy | RuleName | FuncProxy],
	):
		rules: list[RuleName] = []
		for rule in value:
			if isinstance(rule, str):
				rule = RuleName(rule)
			elif hasattr(rule, "name"):
				rule = RuleName(rule.name)
			elif hasattr(rule, "__name__"):
				rule = RuleName(rule.__name__)
			else:
				raise TypeError("Not a rule", rule)
			rules.append(rule)
		self.engine.handle("set_rulebook_rules", rulebook=key, rules=rules)

	def __delitem__(self, key: RulebookName):
		del self._cache[key]
		self.engine.handle("del_rulebook", rulebook=key)


class AllRulesProxy(MutableMapping):
	@property
	def _cache(self):
		return self.engine._rules_cache

	def _worker_check(self):
		self.engine._worker_check()

	def __init__(self, engine_proxy: EngineProxy):
		self.engine = engine_proxy
		self._proxy_cache = {}

	def __iter__(self):
		return iter(self._cache)

	def __len__(self):
		return len(self._cache)

	def __contains__(self, k: RuleName):
		return k in self._cache

	def __getitem__(self, k: RuleName):
		if k not in self:
			raise KeyError("No rule: {}".format(k))
		if k not in self._proxy_cache:
			self._proxy_cache[k] = RuleProxy(self.engine, k)
		return self._proxy_cache[k]

	def __setitem__(self, key: RuleName, value: RuleProxy | FuncProxy | str):
		if isinstance(value, RuleProxy):
			self._proxy_cache[key] = value
		elif callable(value) or hasattr(self.engine.action, value):
			proxy = self._proxy_cache[key] = RuleProxy(self.engine, key)
			proxy.action(value)
		else:
			raise TypeError("Need RuleProxy or an action", type(value))

	def __delitem__(self, key: RuleName):
		self.engine.handle("del_rule", rule=key)
		if key in self._proxy_cache:
			del self._proxy_cache[key]

	def __call__(
		self,
		action: callable | FuncProxy | None = None,
		always: bool = False,
		neighborhood: Optional[int] = None,
	):
		if action is None:
			return partial(self, always=always, neighborhood=neighborhood)
		name = getattr(action, "__name__", action)
		self[name] = action
		ret = self[name]
		if always:
			ret.triggers.append(self.engine.trigger.truth)
		if neighborhood is not None:
			ret.neighborhood = neighborhood
		return ret

	def new_empty(self, k: RuleName) -> RuleProxy:
		self._worker_check()
		self.engine.handle(command="new_empty_rule", rule=k)
		self._cache[k] = {"triggers": [], "prereqs": [], "actions": []}
		self._proxy_cache[k] = RuleProxy(self.engine, k)
		return self._proxy_cache[k]


class FuncProxy(object):
	__slots__ = "store", "name"

	def __init__(self, store: FuncStoreProxy, func: FuncName):
		self.store = store
		self.name = func

	def __call__(
		self,
		*args: Value,
		cb: Optional[callable] = None,
		**kwargs: dict[Key, Value],
	):
		return self.store.engine.handle(
			"call_stored_function",
			store=self.store._store,
			func=self.name,
			args=args[1:] if self.store._store == "method" else args,
			kwargs=kwargs,
			cb=partial(self.store.engine._upd_and_cb, cb=cb),
		)[0]

	def __str__(self):
		return self.store._cache[self.name]


class FuncStoreProxy(Signal):
	_cache: dict

	def _worker_check(self):
		self.engine._worker_check()

	def __init__(self, engine_proxy: EngineProxy, store: FuncStoreName):
		super().__init__()
		self.engine = engine_proxy
		self._store = store
		self._proxy_cache = {}

	def load(self):
		self._cache = self.engine.handle("source_copy", store=self._store)

	def __getattr__(self, k: str) -> FuncProxy:
		if k in super().__getattribute__("_cache"):
			proxcache = super().__getattribute__("_proxy_cache")
			if k not in proxcache:
				proxcache[k] = FuncProxy(self, k)
			return proxcache[k]
		else:
			raise AttributeError(k)

	def __call__(self, func: callable):
		src = getsource(func)
		self.engine.handle(
			"store_source", v=src, name=func.__name__, store=self._store
		)
		funcname = func.__name__
		self._cache[funcname] = src
		self._proxy_cache[funcname] = FuncProxy(self, funcname)

	def __setattr__(self, func_name: str, func: callable | str):
		if func_name in (
			"engine",
			"_store",
			"_cache",
			"_proxy_cache",
			"receivers",
			"_by_sender",
			"_by_receiver",
			"_weak_senders",
			"is_muted",
		):
			super().__setattr__(func_name, func)
			return
		if callable(func):
			source = getsource(func)
		else:
			source = func
		self.engine.handle(
			command="store_source", store=self._store, v=source, name=func_name
		)
		self._cache[func_name] = source

	def __delattr__(self, func_name: str):
		self.engine.handle(
			command="del_source", store=self._store, k=func_name
		)
		del self._cache[func_name]

	def get_source(self, func_name: str) -> str:
		if func_name == "truth":
			return "def truth(*args):\n\treturn True"
		return self.engine.handle(
			command="get_source", store=self._store, name=func_name
		)


class ChangeSignatureError(TypeError):
	pass


class PortalObjCache:
	def __init__(self):
		self.successors = {}
		self.predecessors = {}

	def store(
		self, char: CharName, u: NodeName, v: NodeName, obj: PortalProxy
	) -> None:
		succ = self.successors
		if char in succ:
			if u in succ[char]:
				succ[char][u][v] = obj
			else:
				succ[char][u] = {v: obj}
		else:
			succ[char] = {u: {v: obj}}
		pred = self.predecessors
		if char in pred:
			if v in pred[char]:
				pred[char][v][u] = obj
			else:
				pred[char][v] = {u: obj}
		else:
			pred[char] = {v: {u: obj}}

	def delete(self, char: CharName, u: NodeName, v: NodeName) -> None:
		succ = self.successors
		if char in succ:
			succ_us = succ[char]
			if u in succ_us and v in succ_us[u]:
				del succ_us[u][v]
			if not succ_us[u]:
				del succ_us[u]
			if not succ_us:
				del succ[char]
		pred = self.predecessors
		if char in pred:
			pred_vs = pred[char]
			if v in pred_vs and u in pred_vs[v]:
				del pred_vs[v][u]
			if not pred_vs[v]:
				del pred_vs[v]
			if not pred_vs:
				del pred[char]

	def delete_char(self, char: CharName) -> None:
		if char in self.successors:
			del self.successors[char]
			del self.predecessors[char]


class RandoProxy(Random):
	"""Proxy to a randomizer"""

	def __init__(self, engine: EngineProxy, seed=None):
		self.engine = engine
		self._handle = engine.handle
		self.gauss_next = None
		if seed:
			self.seed(seed)

	def seed(self, a=None, version=2):
		self._handle(
			cmd="call_randomizer", method="seed", a=a, version=version
		)

	def getstate(self):
		return self._handle(cmd="call_randomizer", method="getstate")

	def setstate(self, state):
		return self._handle(
			cmd="call_randomizer", method="setstate", state=state
		)

	def _randbelow(
		self, n, int=int, maxsize=1, type=type, Method=None, BuiltinMethod=None
	):
		return self._handle(
			cmd="call_randomizer", method="_randbelow", n=n, maxsize=maxsize
		)

	def random(self):
		return self._handle(cmd="call_randomizer", method="random")


class NextTurnProxy(Signal):
	def __init__(self, engine: EngineProxy):
		super().__init__()
		self.engine = engine

	def __call__(
		self, cb: Optional[callable] = None
	) -> tuple[list, DeltaDict]:
		return self.engine.handle(
			"next_turn",
			cb=partial(
				self.engine._upd_and_cb, partial(self._send_and_cb, cb)
			),
		)

	def _send_and_cb(self, cb: Optional[callable] = None, *args, **kwargs):
		self.send(self)
		if cb is not None:
			cb(*args, **kwargs)


class BookmarkMappingProxy(AbstractBookmarkMapping, UserDict):
	def __init__(self, engine: EngineProxy):
		self.engine = engine
		super().__init__(self.engine.handle("bookmarks_dump"))

	def __call__(self, key: Key) -> None:
		self.data[key] = self.engine.handle("set_bookmark", key=key)

	def __setitem__(self, key: Key, value: Time):
		if not (
			isinstance(value, tuple)
			and len(tuple) == 3
			and isinstance(tuple[0], str)
			and isinstance(tuple[1], int)
			and isinstance(tuple[2], int)
		):
			raise TypeError("Not a valid time", value)
		self.data[key] = self.engine.handle(
			"set_bookmark", key=key, time=value
		)

	def __delitem__(self, key: Key):
		self.engine.handle("del_bookmark", key=key)
		del self.data[key]


class EngineProxy(AbstractEngine):
	"""An engine-like object for controlling a lisien process

	Don't instantiate this directly. Use :class:`EngineProcessManager` instead.
	The ``start`` method will return an :class:`EngineProxy` instance.

	"""

	char_cls = CharacterProxy
	thing_cls = ThingProxy
	place_cls = PlaceProxy
	portal_cls = PortalProxy
	time = TimeSignalDescriptor()
	is_proxy = True

	@cached_property
	def bookmark(self) -> BookmarkMappingProxy:
		return BookmarkMappingProxy(self)

	def export(
		self, name: str | None, path: str | os.PathLike | None
	) -> str | os.PathLike:
		if name is None and path is None:
			raise ValueError("Need name or path")
		return self.handle("export", name=name, path=path)

	def from_archive(
		cls,
		path: str | os.PathLike,
		prefix: str | os.PathLike | None = ".",
		**kwargs,
	) -> AbstractEngine:
		raise TypeError(
			"You want the ``load_archive`` method of ``EngineProcessManager`` instead"
		)

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.close()

	def _get_node(
		self, char: AbstractCharacter | CharName, node: NodeName
	) -> Node:
		return self.character[char].node[node]

	def _worker_check(self):
		if self._worker and not getattr(self, "_mutable_worker", False):
			raise WorkerProcessReadOnlyError(
				"Tried to change the world state in a worker process"
			)

	def _set_btt(
		self,
		branch: Branch,
		turn: Turn,
		tick: Optional[Tick] = None,
		cb: Optional[callable] = None,
	):
		return self.handle(
			"time_travel",
			branch=branch,
			turn=turn,
			tick=tick,
			cb=partial(self._upd_and_cb, cb=cb),
		)

	def _start_branch(
		self, parent: Branch, branch: Branch, turn: Turn, tick: Tick
	) -> None:
		_, start_turn, start_tick, end_turn, end_tick = self._branches_d[
			parent
		]
		if not (
			(start_turn, start_tick) <= (turn, tick) <= (end_turn, end_tick)
		):
			raise OutOfTimelineError(
				"The parent branch does not cover that time",
				parent,
				turn,
				tick,
			)
		self._branches_d[branch] = (parent, turn, tick, turn, tick)
		self.handle(
			"start_branch", parent=parent, branch=branch, turn=turn, tick=tick
		)

	def _extend_branch(self, branch: Branch, turn: Turn, tick: Tick) -> None:
		parent, start_turn, start_tick, end_turn, end_tick = self._branches_d[
			branch
		]
		if (turn, tick) < (start_turn, start_tick):
			raise OutOfTimelineError(
				"Can't extend branch backwards", branch, turn, tick
			)
		if (turn, tick) < (end_turn, end_tick):
			return
		if not self._planning:
			self._branches_d[branch] = (
				parent,
				start_turn,
				start_tick,
				turn,
				tick,
			)

	def load_at(self, branch: Branch, turn: Turn, tick: Tick) -> None:
		self.handle("load_at", branch=branch, turn=turn, tick=tick)

	def branch_end(self, branch: Optional[Branch] = None):
		return self.handle("branch_end", branch=branch)

	def turn_end(
		self, branch: Optional[Branch] = None, turn: Optional[Turn] = None
	) -> Tick:
		if self._worker:
			raise NotImplementedError("Need to cache turn ends in workers")
		return self.handle("turn_end", branch=branch, turn=turn)

	def turn_end_plan(
		self, branch: Optional[Branch] = None, turn: Optional[Turn] = None
	) -> Tick:
		if self._worker:
			raise NotImplementedError("Need to cache plans in workers")
		return self.handle("turn_end_plan", branch=branch, turn=turn)

	@property
	def trunk(self) -> Branch:
		return self.handle("main_branch")

	@trunk.setter
	def trunk(self, branch: Branch) -> None:
		self._worker_check()
		if self.branch != self.trunk or self.turn != 0 or self._tick != 0:
			raise AttributeError("Go to the start of time first")
		kf = self.handle(
			"switch_main_branch", branch=branch, cb=self._upd_time
		)
		assert self.branch == branch
		self._replace_state_with_kf(kf)

	def snap_keyframe(self) -> Keyframe:
		if self._worker and not getattr(self, "_mutable_worker", False):
			raise WorkerProcessReadOnlyError(
				"Can't snap a keyframe in a worker process"
			)
		return self.handle("snap_keyframe")

	def game_init(self) -> None:
		self._worker_check()
		self.handle("game_init", cb=self._upd_from_game_start)

	def _node_exists(self, char: CharName, node: NodeName) -> bool:
		return self.handle("node_exists", char=char, node=node)

	def _upd_from_game_start(
		self,
		command: str,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		result: tuple,
	):
		(start_kf, eternal, plainstored, pklstored) = result
		self._initialized = False
		self._eternal_cache = eternal
		for name, store in [
			("function", self.function),
			("method", self.method),
			("trigger", self.trigger),
			("prereq", self.prereq),
			("action", self.action),
		]:
			if name in plainstored:
				if isinstance(store, FuncStoreProxy):
					store._cache = plainstored[name]
					self.debug(
						f"Replaced func store proxies for {name} in {store} in worker {self.i}"
					)
				elif isinstance(store, FunctionStore):
					for fname, source in plainstored[name].items():
						store._set_source(fname, source)
						self.debug(
							f"Replaced function {fname} in {store} with plain source in worker {self.i}"
						)
				else:
					self.error(
						f"Can't set {name} on {store} in worker {self.i}"
					)
			elif name in pklstored:
				replacement = pickle.loads(pklstored[name])
				setattr(self, name, replacement)
			elif hasattr(store, "reimport") and callable(store.reimport):
				store.reimport()
		self._replace_state_with_kf(start_kf)
		self._branch = branch
		self._turn = turn
		self._tick = tick
		self._initialized = True

	def _replace_state_with_kf(self, result: Keyframe | None, **kwargs):
		things = self._things_cache
		places = self._character_places_cache

		portals = self._character_portals_cache
		if result is None:
			self._char_cache = {}
			self._universal_cache = {}
			return
		self._universal_cache = result["universal"]
		rc = self._rules_cache = {}
		triggers: list[TriggerFuncName]
		for rule, triggers in result["triggers"].items():
			triglist = []
			if isinstance(self.trigger, FuncStoreProxy):
				for func in triggers:
					if not hasattr(self.trigger, func):
						self.trigger._proxy_cache[func] = FuncProxy(
							self.trigger, func
						)
					triglist.append(getattr(self.trigger, func))
			else:
				for func in triggers:
					if not hasattr(self.trigger, func):
						if isinstance(self.trigger, FuncStoreProxy):
							setattr(
								self.trigger,
								func,
								FuncProxy(self.trigger, func),
							)
						elif hasattr(self.trigger, "reimport"):
							self.trigger.reimport()
					if hasattr(self.trigger, func):
						triglist.append(getattr(self.trigger, func))
					else:
						self.warning(
							f"didn't find {func} in trigger file {self.trigger._filename}"
						)
			if rule in rc:
				rc[rule]["triggers"] = triglist
			else:
				rc[rule] = {
					"triggers": triglist,
					"prereqs": [],
					"actions": [],
				}
		prereqs: list[PrereqFuncName]
		for rule, prereqs in result["prereqs"].items():
			preqlist = []
			if isinstance(self.prereq, FuncStoreProxy):
				for func in prereqs:
					if not hasattr(self.prereq, func):
						self.prereq._proxy_cache[func] = FuncProxy(
							self.prereq, func
						)
					preqlist.append(getattr(self.prereq, func))
			else:
				for func in prereqs:
					if not hasattr(self.prereq, func):
						if isinstance(self.prereq, FuncStoreProxy):
							setattr(
								self.prereq, func, FuncProxy(self.prereq, func)
							)
						elif hasattr(self.prereq, "reimport"):
							self.prereq.reimport()
					if hasattr(self.prereq, func):
						preqlist.append(getattr(self.prereq, func))
					else:
						self.warning(
							f"didn't find {func} in prereq file {self.prereq._filename}"
						)
			if rule in rc:
				rc[rule]["prereqs"] = preqlist
			else:
				rc[rule] = {
					"triggers": [],
					"prereqs": preqlist,
					"actions": [],
				}
		actions: list[ActionFuncName]
		for rule, actions in result["actions"].items():
			actlist = []
			if isinstance(self.action, FuncStoreProxy):
				for func in actions:
					if not hasattr(self.action, func):
						self.action._proxy_cache[func] = FuncProxy(
							self.action, func
						)
					actlist.append(getattr(self.action, func))
			else:
				for func in actions:
					if not hasattr(self.action, func) and hasattr(
						self.action, "reimport"
					):
						self.action.reimport()
					if hasattr(self.action, func):
						actlist.append(getattr(self.action, func))
					else:
						self.warning(
							f"didn't find {func} in action file {self.action._filename}"
						)
			if rule in rc:
				rc[rule]["actions"] = actlist
			else:
				rc[rule] = {
					"triggers": [],
					"prereqs": [],
					"actions": actlist,
				}
		self._rulebooks_cache = result["rulebook"]
		self._char_cache = chars = {
			graph: CharacterProxy(self, graph)
			if (graph not in self._char_cache)
			else self._char_cache[graph]
			for graph in (
				result["graph_val"].keys()
				| result["nodes"].keys()
				| result["node_val"].keys()
				| result["edges"].keys()
				| result["edge_val"].keys()
				| self._char_cache.keys()
			)
		}
		for graph, stats in result["graph_val"].items():
			if "character_rulebook" in stats:
				self._character_rulebooks_cache[graph]["character"] = (
					stats.pop("character_rulebook")
				)
			if "unit_rulebook" in stats:
				self._character_rulebooks_cache[graph]["unit"] = stats.pop(
					"unit_rulebook"
				)
			if "character_thing_rulebook" in stats:
				self._character_rulebooks_cache[graph]["thing"] = stats.pop(
					"character_thing_rulebook"
				)
			if "character_place_rulebook" in stats:
				self._character_rulebooks_cache[graph]["place"] = stats.pop(
					"character_place_rulebook"
				)
			if "character_portal_rulebook" in stats:
				self._character_rulebooks_cache[graph]["portal"] = stats.pop(
					"character_portal_rulebook"
				)
			if "units" in stats:
				self._character_units_cache[graph] = stats.pop("units")
			else:
				self._character_units_cache[graph] = {}
			self._char_stat_cache[graph] = stats
		nodes_to_delete = {
			(char, node)
			for char in things.keys() | places.keys()
			for node in things.get(char, {}).keys()
			| places.get(char, {}).keys()
		}
		for char, nodes in result["nodes"].items():
			nodes: NodesDict
			for node, ex in nodes.items():
				if ex:
					if not (
						(char in things and node in things[char])
						or (char in places and node in places[char])
					):
						places[char][node] = PlaceProxy(chars[char], node)
					nodes_to_delete.discard((char, node))
				else:
					if char in things and node in things[char]:
						del things[char][node]
					if char in places and node in places[char]:
						del places[char][node]
		for char, node in nodes_to_delete:
			if node in things[char]:
				del things[char][node]
			else:
				del places[char][node]
		for char, nodestats in result["node_val"].items():
			nodestats: NodeValDict
			for node, stats in nodestats.items():
				if "location" in stats:
					if char not in things or node not in things[char]:
						things[char][node] = ThingProxy(
							chars[char],
							node,
							NodeName(Key(stats.pop("location"))),
						)
					else:
						things[char][node]._location = NodeName(
							Key(stats.pop("location"))
						)
					if char in places and node in places[char]:
						del places[char][node]
				else:
					if char not in places or node not in places[char]:
						places[char][node] = PlaceProxy(chars[char], node)
					if char in things and node in things[char]:
						del things[char][node]
				self._node_stat_cache[char][node] = stats
		edges_to_delete = {
			(char, orig, dest)
			for char in portals.successors
			for orig in portals.successors[char]
			for dest in portals.successors[char][orig]
		}
		for char, origs in result["edges"].items():
			origs: EdgesDict
			for orig, dests in origs.items():
				for dest, exists in dests.items():
					if (
						char in portals.successors
						and orig in portals.successors[char]
						and dest in portals.successors[char][orig]
					):
						if exists:
							edges_to_delete.discard((char, orig, dest))
						else:
							del portals.successors[char][orig][dest]
							del portals.predecessors[char][dest][orig]
						continue
					if exists:
						edges_to_delete.discard((char, orig, dest))
					else:
						continue
					that = PortalProxy(chars[char], orig, dest)
					portals.store(char, orig, dest, that)
		for char, orig, dest in edges_to_delete:
			portals.delete(char, orig, dest)
		for char, origs in result["edge_val"].items():
			origs: EdgeValDict
			for orig, dests in origs.items():
				for dest, stats in dests.items():
					self._portal_stat_cache[char][orig][dest] = stats

	def _pull_kf_now(self, *args, **kwargs):
		self._replace_state_with_kf(self.handle("snap_keyframe"))

	@property
	def branch(self) -> Branch:
		return self._branch

	@branch.setter
	def branch(self, v: Branch):
		if v not in self._branches_d:
			self._start_branch(self.branch, v, self.turn, self.tick)
		self._set_btt(v, self.turn)

	@property
	def turn(self) -> Turn:
		return self._turn

	@turn.setter
	def turn(self, v: int):
		if not isinstance(v, int):
			raise TypeError("Turns must be integers")
		if v < 0:
			raise ValueError("Turns can't be negative")
		if v == self.turn:
			return
		v = Turn(v)
		turn_end, tick_end = self._branch_end()
		if (
			self._enforce_end_of_time
			and not self._planning
			and (v, self.tick) > (turn_end, tick_end)
		):
			raise OutOfTimelineError(
				f"The turn {v} is after the end of the branch {self.branch}. "
				f"Go to turn {turn_end} and simulate with `next_turn`.",
				self.branch,
				self.turn,
				self.tick,
				self.branch,
				v,
				self.tick,
			)
		branch = self.branch
		if self._planning:
			tick = self.turn_end_plan()
		else:
			tick = self.turn_end()
		self._extend_branch(branch, v, tick)
		self._set_btt(branch, v)

	@property
	def tick(self) -> Tick:
		return self._tick

	@tick.setter
	def tick(self, v: Tick):
		if not isinstance(v, int):
			raise TypeError("Ticks must be integers")
		if v < 0:
			raise ValueError("Ticks can't be negative")
		if v == self.tick:
			return
		v = Tick(v)
		if self._enforce_end_of_time:
			if self._planning:
				end_turn, end_tick = self.handle(
					"branch_end_plan_turn_and_tick"
				)
			else:
				end_turn, end_tick = (
					self.branch_end_turn(),
					self.branch_end_tick(),
				)
			if (self.turn, v) > (end_turn, end_tick):
				raise OutOfTimelineError(
					f"Tick {v} of turn {self.turn} is after the end of the branch"
					f" {self.branch}. "
					f"Simulate with `next_turn`.",
					self.branch,
					self.turn,
					self.tick,
					self.branch,
					v,
					self.tick,
				)
		self._set_btt(self.branch, self.turn, v)

	def _btt(self) -> Time:
		return self._branch, self._turn, self._tick

	def __init__(
		self,
		pipe_in: Connection | Queue | SimpleQueue,
		pipe_out: Connection | Queue | SimpleQueue,
		logger: logging.Logger,
		install_modules=(),
		submit_func: callable = None,
		threads: int = None,
		prefix: str | os.PathLike = None,
		worker_index: int = None,
		replay_file: str | os.PathLike | io.TextIOBase = None,
		eternal: dict = None,
		universal: dict = None,
		branches: dict = None,
		function: dict = None,
		method: dict = None,
		trigger: dict = None,
		prereq: dict = None,
		action: dict = None,
		enforce_end_of_time: bool = True,
	):
		if eternal is None:
			eternal = {"language": "eng"}
		if universal is None:
			universal = {"rando_state": random.getstate()}
		if branches is None:
			branches = {"trunk": (None, 0, 0, 0, 0)}
		self._planning: bool = False
		self._enforce_end_of_time: bool = enforce_end_of_time
		self._eternal_cache: dict[EternalKey, Value] = eternal
		self._universal_cache: dict[UniversalKey, Value] = universal
		self._rules_cache: dict[
			RuleName,
			dict[
				Literal["triggers", "prereqs", "actions"],
				list[TriggerFuncName]
				| list[PrereqFuncName]
				| list[ActionFuncName],
			],
		] = {}
		self._neighborhood_cache: dict[RuleName, RuleNeighborhood] = {}
		self._rulebooks_cache: dict[
			RulebookName, tuple[list[RuleName], RulebookPriority]
		] = {}
		self._branches_d: dict[
			Branch, tuple[Branch | None, Turn, Tick, Turn, Tick]
		] = branches
		self._planning: bool = False
		if replay_file is not None:
			if not isinstance(replay_file, io.TextIOBase):
				if os.path.exists(replay_file):
					with open(replay_file, "rt") as rf:
						self._replay_txt = rf.read().replace(
							"<lisien.proxy.EngineProxy>", "eng"
						)
				else:
					self._replay_file = open(replay_file, "wt")
			elif hasattr(replay_file, "mode"):
				if "w" in replay_file.mode or "a" in replay_file.mode:
					self._replay_file = replay_file
				elif "r" in replay_file.mode:
					self._replay_txt = replay_file.read().replace(
						"<lisien.proxy.EngineProxy>", "eng"
					)
				else:
					self.error(
						"Can't open replay file, mode "
						+ repr(replay_file.mode)
					)
			else:
				txt = replay_file.read()
				if not txt:
					self._replay_file = replay_file
					self.warning(
						"Recording replay to an io object with no mode"
					)
				else:
					self._replay_txt = txt.replace(
						"<lisien.proxy.EngineProxy>", "eng"
					)
		self.i: int | None = worker_index
		self.closed: bool = False
		if submit_func:
			self._submit = submit_func
		else:
			self._threadpool = ThreadPoolExecutor(threads)
			self._submit = self._threadpool.submit
		self._pipe_out = pipe_out
		self._pipe_out_lock = Lock()
		self._pipe_in = pipe_in
		self._pipe_in_lock = Lock()
		self._round_trip_lock = Lock()
		self._commit_lock = Lock()
		self.logger = logger
		self.character = self.graph = CharacterMapProxy(self)
		self.eternal = EternalVarProxy(self)
		self.universal = GlobalVarProxy(self)
		self.rulebook = AllRuleBooksProxy(self)
		self.rule = AllRulesProxy(self)
		if worker_index is None:
			self.logger.debug("EngineProxy: starting proxy to core")
			self._worker = False
			self.next_turn = NextTurnProxy(self)
			self.method = FuncStoreProxy(self, "method")
			self.action = FuncStoreProxy(self, "action")
			self.prereq = FuncStoreProxy(self, "prereq")
			self.trigger = FuncStoreProxy(self, "trigger")
			self.function = FuncStoreProxy(self, "function")
			self._rando = RandoProxy(self)
			self.string = StringStoreProxy(self)
		else:
			self.debug("EngineProxy: starting worker %d" % worker_index)
			self._worker = True
			self._worker_idx = worker_index
			if getattr(self, "_mutable_worker", False):

				def next_turn():
					raise WorkerProcessReadOnlyError(
						"Can't advance time in a worker process"
					)

				self.next_turn = next_turn
			else:
				self._rando = Random()
				self.next_turn = lambda: None
			self.method = FunctionStore(
				os.path.join(prefix, "method.py") if prefix else None,
				initial=method,
			)
			self.action = FunctionStore(
				os.path.join(prefix, "action.py") if prefix else None,
				initial=action,
			)
			self.prereq = FunctionStore(
				os.path.join(prefix, "prereq.py") if prefix else None,
				initial=prereq,
			)
			self.trigger = FunctionStore(
				os.path.join(prefix, "trigger.py") if prefix else None,
				initial=trigger,
			)
			self.function = FunctionStore(
				os.path.join(prefix, "function.py") if prefix else None,
				initial=function,
			)
			self.string = StringStore(self, prefix)

		self._node_stat_cache = StructuredDefaultDict(1, UnwrappingDict)
		self._portal_stat_cache = StructuredDefaultDict(2, UnwrappingDict)
		self._char_stat_cache = PickyDefaultDict(UnwrappingDict)
		self._things_cache = StructuredDefaultDict(1, ThingProxy)
		self._character_places_cache = StructuredDefaultDict(1, PlaceProxy)
		self._character_rulebooks_cache = StructuredDefaultDict(
			1,
			Key,
			kwargs_munger=lambda inst, k: {
				"engine": self,
				"bookname": (inst.key, k),
			},
		)
		self._char_node_rulebooks_cache = StructuredDefaultDict(
			1,
			Key,
			kwargs_munger=lambda inst, k: {
				"engine": self,
				"bookname": (inst.key, k),
			},
		)
		self._char_port_rulebooks_cache = StructuredDefaultDict(
			2,
			Key,
			kwargs_munger=lambda inst, k: {
				"engine": self,
				"bookname": (inst.parent.key, inst.key, k),
			},
		)
		self._character_portals_cache = PortalObjCache()
		self._character_units_cache = PickyDefaultDict(dict)
		self._unit_characters_cache = PickyDefaultDict(dict)
		self._rule_obj_cache = {}
		self._rulebook_obj_cache = {}
		self._char_cache = {}
		self._install_modules = install_modules
		self.debug("EngineProxy: finished core __init__")

	def _init_pull_from_core(self):
		self.debug("EngineProxy: Waiting for core...")
		received = self.recv()
		self.debug(f"EngineProxy: Got time: {received}")
		self._branch, self._turn, self._tick = received[-1]
		self.debug("EngineProxy: Getting branches...")
		self.send({"command": "branches"})
		self._branches_d = self.recv()[-1]
		self.debug(f"Got {len(self._branches_d)} branches")
		self.method.load()
		self.action.load()
		self.prereq.load()
		self.trigger.load()
		self.trigger._cache["truth"] = "def truth(obj):\n\treturn True"
		self.function.load()
		self._eternal_cache = self.handle("eternal_copy")
		self.debug(f"Got {len(self._eternal_cache)} eternal vars")
		self._initialized = False
		self._pull_kf_now()
		self._initialized = True
		for module in self._install_modules:
			self.handle("install_module", module=module)
			self.debug(f"Installed module: {module}")
		if hasattr(self, "_replay_txt"):
			replay = ast.parse(self._replay_txt)
			for expr in replay.body:
				if isinstance(expr.value, ast.Call):
					method = expr.value.func.id
					args = []
					kwargs = {}
					for arg in expr.value.args:
						if isinstance(arg.value, ast.Subscript):
							whatmap = arg.value.value.attr
							key = arg.value.slice.value
							args.append(getattr(self, whatmap)[key])
						elif hasattr(arg.value, "value"):
							args.append(arg.value.value)
						else:
							args.append(unparse(arg.value))
					for kw in expr.value.keywords:
						if isinstance(kw.value, ast.Subscript):
							whatmap = kw.value.value.attr
							key = kw.value.slice.value
							kwargs[kw.arg] = getattr(self, whatmap)[key]
						else:
							if hasattr(kw.value, "value"):
								kwargs[kw.arg] = kw.value.value
							else:
								kwargs[kw.arg] = unparse(kw.value)
					self.handle(method, *args, **kwargs)

	def __repr__(self):
		return "<lisien.proxy.EngineProxy>"

	def __getattr__(self, item):
		method = super().__getattribute__("method")
		try:
			meth = method.__getattr__(item)
		except AttributeError:
			if not hasattr(method, "reimport"):
				raise
			try:
				method.reimport()
			except FileNotFoundError:
				pass
			try:
				meth = method.__getattr__(item)
			except AttributeError:
				raise AttributeError(
					"lisien.proxy.EngineProxy does not have the attribute",
					item,
				)
		return MethodType(meth, self)

	def _reimport_triggers(self) -> None:
		if hasattr(self.trigger, "reimport"):
			self.trigger.reimport()

	def _replace_triggers_pkl(self, replacement: bytes) -> None:
		assert self._worker, "Loaded replacement triggers outside a worker"
		self.trigger._locl = pickle.loads(replacement)

	def _eval_trigger(self, name, entity) -> None:
		return getattr(self.trigger, name)(entity)

	def _call_function(self, name: FuncName, *args, **kwargs):
		return getattr(self.function, name)(*args, **kwargs)

	def _reimport_functions(self) -> None:
		if hasattr(self.function, "reimport"):
			self.function.reimport()

	def _replace_functions_pkl(self, replacement: bytes) -> None:
		assert self._worker, "Loaded replacement functions outside a worker"
		self.function._locl = pickle.loads(replacement)

	def _call_method(self, name: FuncName, *args, **kwargs):
		return MethodType(getattr(self.method, name), self)(*args, **kwargs)

	def _reimport_methods(self) -> None:
		if hasattr(self.method, "reimport"):
			self.method.reimport()

	def _replace_methods_pkl(self, replacement: bytes) -> None:
		assert self._worker, "Loaded replacement methods outside a worker"
		self.method._locl = pickle.loads(replacement)

	def send(
		self, obj: Value, blocking: bool = True, timeout: int | float = 1
	) -> None:
		if hasattr(self._pipe_in, "send_bytes"):
			self.send_bytes(self.pack(obj), blocking=blocking, timeout=timeout)
		else:
			self.debug(f"EngineProxy: putting {obj} into _handle_in")
			self._pipe_in.put(obj, timeout=timeout)

	def send_bytes(self, obj: bytes, blocking=True, timeout=1) -> None:
		if not isinstance(self._pipe_out, Connection):
			raise TypeError("Tried to send bytes not between processes")
		compressed = zlib.compress(obj)
		self._pipe_out_lock.acquire(blocking, timeout)
		self._pipe_out.send_bytes(compressed)
		self._pipe_out_lock.release()

	def recv_bytes(self, blocking=True, timeout=1) -> bytes:
		if not isinstance(self._pipe_in, Connection):
			raise TypeError("Tried to receive bytes not from another process")
		self._pipe_in_lock.acquire(blocking, timeout)
		data = self._pipe_in.recv_bytes()
		self._pipe_in_lock.release()
		return zlib.decompress(data)

	def recv(self, blocking: bool = True, timeout: int | float = 1) -> Value:
		if hasattr(self._pipe_out, "recv_bytes"):
			return self.unpack(
				self.recv_bytes(blocking=blocking, timeout=timeout)
			)
		else:
			return self._pipe_out.get()

	def debug(self, msg: str) -> None:
		self.logger.debug(msg)

	def info(self, msg: str) -> None:
		self.logger.info(msg)

	def warning(self, msg: str) -> None:
		self.logger.warning(msg)

	def error(self, msg: str) -> None:
		self.logger.error(msg)

	def critical(self, msg: str) -> None:
		self.logger.critical(msg)

	def handle(self, cmd: str | None = None, *, cb: callable = None, **kwargs):
		"""Send a command to the lisien core.

		The only positional argument should be the name of a
		method in :class:``EngineHandle``. All keyword arguments
		will be passed to it, with the exceptions of
		``cb``, ``branching``, and ``silent``.

		With ``branching=True``, handle paradoxes by creating new
		branches of history. I will switch to the new branch if needed.
		If I have an attribute ``branching_cb``, I'll call it if and
		only if the branch changes upon completing a command with
		``branching=True``.

		With a function ``cb``, I will call ``cb`` when I get
		a result.
		``cb`` will be called with keyword arguments ``command``,
		the same command you asked for; ``result``, the value returned
		by it, possibly ``None``; and the present ``branch``,
		``turn``, and ``tick``, possibly different than when you called
		``handle``.`.

		"""
		then = self._btt()
		if self._worker or getattr(self, "_mutable_worker", False):
			return
		if self.closed:
			raise RuntimeError(f"Already closed: {id(self)}")
		if "command" in kwargs:
			cmd = kwargs["command"]
		elif cmd:
			kwargs["command"] = cmd
		else:
			raise TypeError("No command")
		assert not kwargs.get("silent")
		if hasattr(self, "_replay_file"):
			self._replay_file.write(repr_call_sig(cmd, **kwargs) + "\n")
		start_ts = monotonic()
		with self._round_trip_lock:
			self.send(Value(kwargs))
			received = self.recv()
			command, branch, turn, tick, r = received
		self.debug(
			"EngineProxy: received {} in {:,.2f} seconds".format(
				(command, branch, turn, tick), monotonic() - start_ts
			)
		)
		if (branch, turn, tick) != then:
			self._upd_time(command, branch, turn, tick, r)
		if isinstance(r, Exception):
			raise r
		if cmd != command:
			raise RuntimeError(
				f"Sent command {cmd}, but received results for {command}"
			)
		if cb:
			cb(command=command, branch=branch, turn=turn, tick=tick, result=r)
		return r

	def _unpack_recv(self):
		ret = self.unpack(self.recv_bytes())
		return ret

	def _callback(self, cb: callable) -> tuple[str, Branch, Turn, Tick, Value]:
		command, branch, turn, tick, res = self.unpack(self.recv_bytes())
		self.debug(
			"EngineProxy: received, with callback {}: {}".format(
				cb, (command, branch, turn, tick, res)
			)
		)
		ex = None
		if isinstance(res, Exception):
			ex = res
		try:
			if isinstance(res[0], Exception):
				ex = res[0]
		except TypeError:
			pass
		if ex:
			self.warning(
				"{} raised by command {}, trying to run callback {} with it".format(
					repr(ex), command, cb
				)
			)
		cb(command=command, branch=branch, turn=turn, tick=tick, result=res)
		return command, branch, turn, tick, res

	def _branching(
		self, cb: callable | None = None
	) -> tuple[str, Branch, Turn, Tick, Value]:
		command, branch, turn, tick, r = self.unpack(self.recv_bytes())
		self.debug(
			"EngineProxy: received, with branching, {}".format(
				(command, branch, turn, tick, r)
			)
		)
		if (branch, turn, tick) != (self._branch, self._turn, self._tick):
			self._upd_time(command, branch, turn, tick, r)
			self.time.send(self, branch=branch, turn=turn, tick=tick)
			if hasattr(self, "branching_cb"):
				self.branching_cb(
					command=command,
					branch=branch,
					turn=turn,
					tick=tick,
					result=r,
				)
		if cb:
			cb(command=command, branch=branch, turn=turn, tick=tick, result=r)
		return command, branch, turn, tick, r

	def _call_with_recv(self, *cbs: callable, **kwargs) -> Value:
		cmd, branch, turn, tick, received = self.unpack(self.recv_bytes())
		self.debug(
			"EngineProxy: received {}".format(
				(cmd, branch, turn, tick, received)
			)
		)
		if isinstance(received, Exception):
			raise received
		for cb in cbs:
			cb(
				command=cmd,
				branch=branch,
				turn=turn,
				tick=tick,
				result=received,
				**kwargs,
			)
		return received

	def _upd_caches(self, command, branch, turn, tick, result) -> None:
		result, deltas = result
		self.eternal._update_cache(deltas.pop("eternal", {}))
		self.universal._update_cache(deltas.pop("universal", {}))
		# I think if you travel back to before a rule was created
		# it'll show up empty.
		# That's ok I guess
		for rule, delta in deltas.pop("rules", {}).items():
			rule_cached = self._rules_cache.setdefault(rule, {})
			for funcl in ("triggers", "prereqs", "actions"):
				if funcl in delta:
					func_proxies = []
					store = getattr(self, funcl[:-1])
					if delta[funcl] is ...:
						if funcl in rule_cached:
							del rule_cached[funcl]
						continue
					for func in delta[funcl]:
						if hasattr(store, func):
							func_proxy = getattr(store, func)
						else:
							func_proxy = FuncProxy(store, func)
							if hasattr(store, "_proxy_cache"):
								store._proxy_cache[func] = func_proxy
							else:
								# why can this even happen??
								store._proxy_cache = {func: func_proxy}
							if hasattr(store, "_cache"):
								store._cache[func] = store.get_source(func)
							else:
								store._cache = {func: store.get_source(func)}
						func_proxies.append(func_proxy)
					rule_cached[funcl] = func_proxies
			if rule not in self._rule_obj_cache:
				self._rule_obj_cache[rule] = RuleProxy(self, rule)
			ruleproxy = self._rule_obj_cache[rule]
			ruleproxy.send(ruleproxy, **delta)
		rulebookdeltas = deltas.pop("rulebooks", {})
		self._rulebooks_cache.update(rulebookdeltas)
		for rulebook, delta in rulebookdeltas.items():
			if rulebook not in self._rulebook_obj_cache:
				self._rulebook_obj_cache[rulebook] = RuleBookProxy(
					self, rulebook
				)
			rulebookproxy = self._rulebook_obj_cache[rulebook]
			# the "delta" is just the rules list, for now
			rulebookproxy.send(rulebookproxy, rules=delta)
		to_delete = set()
		for char, chardelta in deltas.items():
			if chardelta is None:
				to_delete.add(char)
				continue
			if char not in self._char_cache:
				self._char_cache[char] = CharacterProxy(self, char)
			chara = self.character[char]
			chara._apply_delta(chardelta)
		for char in to_delete & self._char_cache.keys():
			del self._char_cache[char]

	def _upd_time(self, command, branch, turn, tick, result, **kwargs) -> None:
		then = self._btt()
		self._branch = branch
		self._turn = turn
		self._tick = tick
		if not self._planning:
			if branch not in self._branches_d:
				self._branches_d[branch] = (None, turn, tick, turn, tick)
			else:
				self._extend_branch(branch, turn, tick)
		self.time.send(self, then=then, now=(branch, turn, tick))

	@contextmanager
	def plan(self):
		self._planning = True
		yield self.handle("start_plan")
		self.handle("end_plan", cb=self._upd)
		self._planning = False

	def apply_choices(
		self,
		choices: list[dict],
		dry_run: bool = False,
		perfectionist: bool = False,
	) -> Value:
		if self._worker and not getattr(self, "_mutable_worker", False):
			raise WorkerProcessReadOnlyError(
				"Tried to change the world state in a worker process"
			)
		return self.handle(
			"apply_choices",
			choices=choices,
			dry_run=dry_run,
			perfectionist=perfectionist,
		)

	def _reimport_all(self) -> None:
		for store in (
			self.function,
			self.method,
			self.prereq,
			self.trigger,
			self.action,
		):
			if hasattr(store, "reimport"):
				store.reimport()

	def _replace_funcs_pkl(
		self,
		*,
		function: Optional[bytes] = None,
		method: Optional[bytes] = None,
		trigger: Optional[bytes] = None,
		prereq: Optional[bytes] = None,
		action: Optional[bytes] = None,
	) -> None:
		assert self._worker, "Replaced code outside of a worker"
		if function:
			self.function._cache = pickle.loads(function)
		if method:
			self.method._cache = pickle.loads(method)
		if trigger:
			self.trigger._cache = pickle.loads(trigger)
		if prereq:
			self.prereq._cache = pickle.loads(prereq)
		if action:
			self.action._cache = pickle.loads(action)

	def _replace_funcs_plain(
		self,
		*,
		function: Optional[dict[str, str]] = None,
		method: Optional[dict[str, str]] = None,
		trigger: Optional[dict[str, str]] = None,
		prereq: Optional[dict[str, str]] = None,
		action: Optional[dict[str, str]] = None,
	) -> None:
		assert self._worker, "Replaced code outside of a worker"
		for name, store, upd in [
			("function", self.function, function),
			("method", self.method, method),
			("trigger", self.trigger, trigger),
			("prereq", self.prereq, prereq),
			("action", self.action, action),
		]:
			if upd is None:
				continue
			for funcname, source in upd.items():
				store._set_source(funcname, source)

	def _upd(self, *args, **kwargs) -> None:
		to_replace_pkl = kwargs.pop("_replace_funcs_pkl", {})
		to_replace_plain = kwargs.pop("_replace_funcs_plain", {})
		if to_replace_pkl or to_replace_plain:
			assert self._worker, "Replaced code outside of a worker"
			if to_replace_pkl:
				self._replace_funcs_pkl(**to_replace_pkl)
			if to_replace_plain:
				self._replace_funcs_plain(**to_replace_plain)
		else:
			self._reimport_all()
		self._upd_caches(*args, **kwargs)
		self._upd_time(*args, no_del=True, **kwargs)

	def _upd_and_cb(self, cb: callable, *args, **kwargs) -> None:
		self._upd(*args, **kwargs)
		if cb:
			cb(*args, **kwargs)

	def _add_character(
		self,
		char: CharName,
		data: CharDelta | nx.Graph = None,
		layout: bool = False,
		node: NodeValDict | None = None,
		edge: EdgeValDict | None = None,
		**attr: StatDict,
	):
		if char in self._char_cache:
			raise KeyError("Character already exists")
		if isinstance(data, dict):
			try:
				data = nx.from_dict_of_lists(data)
			except nx.NetworkXException:
				data = nx.from_dict_of_dicts(data)
		if data is not None:
			if not isinstance(data, nx.Graph):
				raise TypeError("Need dict or graph", type(data))
			elif data.is_multigraph():
				raise TypeError("No multigraphs")
			if not data.is_directed():
				data = data.to_directed()
		self._char_cache[char] = character = CharacterProxy(self, char)
		self._char_stat_cache[char] = attr
		placedata = {}
		thingdata = {}
		if data:
			for k, v in data.nodes.items():
				if "location" in v:
					thingdata[k] = v
				else:
					placedata[k] = v
		if node:
			for n, v in node.items():
				if "location" in v:
					thingdata[n] = v
				else:
					placedata[n] = v
		for place, stats in placedata.items():
			if (
				char not in self._character_places_cache
				or place not in self._character_places_cache[char]
			):
				self._character_places_cache[char][place] = PlaceProxy(
					character, place
				)
			self._node_stat_cache[char][place] = stats
		for thing, stats in thingdata.items():
			if "location" not in stats:
				raise ValueError("Things must always have locations")
			loc = stats.pop("location")
			if (
				char not in self._things_cache
				or thing not in self._things_cache[char]
			):
				self._things_cache[char][thing] = ThingProxy(
					character, thing, loc
				)
			self._node_stat_cache[char][thing] = stats
		portdata = edge or {}
		if data:
			for orig, dest in data.edges:
				if orig in portdata:
					portdata[orig][dest] = {}
				else:
					portdata[orig] = {dest: {}}
		for orig, dests in portdata.items():
			for dest, stats in dests.items():
				self._character_portals_cache.store(
					char,
					orig,
					dest,
					PortalProxy(character, orig, dest),
				)
				self._portal_stat_cache[char][orig][dest] = stats
		self.handle(
			command="add_character",
			char=char,
			data=data,
			**attr,
			branching=True,
		)

	def add_character(
		self,
		char: Key,
		data: CharDelta | None = None,
		layout: bool = False,
		node: NodeValDict | None = None,
		edge: EdgeValDict | None = None,
		**attr: StatDict,
	):
		if self._worker and not getattr(self, "_mutable_worker", False):
			raise WorkerProcessReadOnlyError(
				"Tried to change world state in a worker process"
			)
		self._add_character(CharName(char), data, layout, node, edge, **attr)

	def new_character(
		self,
		char: Key,
		data: CharDelta | None = None,
		layout: bool = False,
		node: NodeValDict | None = None,
		edge: EdgeValDict | None = None,
		**attr: StatDict,
	):
		char = CharName(char)
		self.add_character(char, data, layout, node, edge, **attr)
		return self._char_cache[char]

	def _del_character(self, char: CharName) -> None:
		if char not in self._char_cache:
			raise KeyError("No such character")
		del self._char_cache[char]
		if char in self._char_stat_cache:
			del self._char_stat_cache[char]
		if char in self._character_places_cache:
			del self._character_places_cache[char]
		if char in self._things_cache:
			del self._things_cache[char]
		self._character_portals_cache.delete_char(char)
		self.handle(command="del_character", char=char, branching=True)

	def del_character(self, char: Key) -> None:
		if self._worker and not getattr(self, "_mutable_worker", False):
			raise WorkerProcessReadOnlyError(
				"tried to change world state in a worker process"
			)
		self._del_character(CharName(char))

	del_graph = del_character

	def del_node(self, char: Key, node: NodeName) -> None:
		char = CharName(char)
		if char not in self._char_cache:
			raise KeyError("No such character")
		if (
			node not in self._character_places_cache[char]
			and node not in self._things_cache[char]
		):
			raise KeyError("No such node")
		cont = list(self._node_contents(char, node))
		if node in self._things_cache[char]:
			del self._things_cache[char][node]
		for contained in cont:
			del self._things_cache[char][contained]
		if node in self._character_places_cache[char]:  # just to be safe
			del self._character_places_cache[char][node]
		successors = self._character_portals_cache.successors
		predecessors = self._character_portals_cache.predecessors
		if char in successors and node in successors[char]:
			del successors[char][node]
			if not successors[char]:
				del successors[char]
		if char in predecessors and node in predecessors[char]:
			del predecessors[char][node]
			if not predecessors[char]:
				del predecessors[char]
		nv = self._node_stat_cache
		if char in nv and node in nv[char]:
			del nv[char][node]
			if not nv[char]:
				del nv[char]
		self.handle(command="del_node", char=char, node=node, branching=True)

	def del_portal(self, char: Key, orig: NodeName, dest: NodeName) -> None:
		char = CharName(char)
		if char not in self._char_cache:
			raise KeyError("No such character")
		self._character_portals_cache.delete(char, orig, dest)
		ev = self._portal_stat_cache
		if char in ev and orig in ev[char] and dest in ev[char][orig]:
			del ev[char][orig][dest]
			if not ev[char][orig]:
				del ev[char][orig]
			if not ev[char]:
				del ev[char]
		self.handle(
			command="del_portal",
			char=char,
			orig=orig,
			dest=dest,
			branching=True,
		)

	def commit(self):
		self._commit_lock.acquire()
		self.handle("commit", cb=self._release_commit_lock)

	def _release_commit_lock(self, *, command, branch, turn, tick, result):
		self._commit_lock.release()

	def close(self) -> None:
		if getattr(self, "closed", False):
			return
		self._commit_lock.acquire()
		self._commit_lock.release()
		self.handle("close")
		self.closed = True

	def _node_contents(
		self, character: CharName, node: NodeName
	) -> Iterator[NodeName]:
		# very slow. do better
		for thing in self.character[character].thing.values():
			if thing["location"] == node:
				yield thing.name


def _finish_packing(pack, cmd, branch, turn, tick, mostly_bytes):
	r = mostly_bytes
	resp = msgpack.Packer().pack_array_header(5)
	resp += pack(cmd) + pack(branch) + pack(turn) + pack(tick)
	if isinstance(r, dict):
		resp += msgpack.Packer().pack_map_header(len(r))
		for k, v in r.items():
			resp += k + v
	elif isinstance(r, tuple):
		pacr = msgpack.Packer()
		pacr.pack_ext_type(
			MsgpackExtensionType.tuple.value,
			msgpack.Packer().pack_array_header(len(r)) + b"".join(r),
		)
		resp += pacr.bytes()
	elif isinstance(r, list):
		resp += msgpack.Packer().pack_array_header(len(r)) + b"".join(r)
	else:
		resp += r
	return resp


def _engine_subroutine_step(
	handle: EngineHandle, instruction: dict, send_output, send_output_bytes
):
	silent = instruction.pop("silent", False)
	cmd = instruction.pop("command")
	branching = instruction.pop("branching", False)
	command = getattr(handle, cmd)
	builtins = __builtins__.copy()
	builtins["set"] = OrderlySet
	builtins["frozenset"] = OrderlyFrozenSet
	globls = globals().copy()
	globls["__builtins__"] = builtins
	r = None

	def do_it():
		return eval(
			"command(**instruction)",
			globls,
			{"command": command, "instruction": instruction},
		)

	try:
		if branching:
			try:
				r = do_it()
			except OutOfTimelineError:
				handle.increment_branch()
				r = do_it()
		else:
			r = do_it()
	except AssertionError:
		raise
	except Exception as ex:
		handle._real.logger.error(repr(ex))
		send_output(cmd, ex)
		return
	if silent:
		return
	if hasattr(getattr(handle, cmd), "prepacked"):
		send_output_bytes(cmd, r)
	else:
		send_output(cmd, r)
	if hasattr(handle, "_after_ret"):
		handle._after_ret()
		del handle._after_ret


def engine_subprocess(
	args, kwargs, input_pipe, output_pipe, *, log_queue=None
):
	"""Loop to handle one command at a time and pipe results back"""

	def send_output(cmd, r):
		output_pipe.send_bytes(
			zlib.compress(
				engine_handle.pack((cmd, *engine_handle._real.time, r))
			)
		)

	def send_output_bytes(cmd, r):
		output_pipe.send_bytes(
			zlib.compress(
				_finish_packing(
					engine_handle.pack, cmd, *engine_handle._real.time, r
				)
			)
		)

	engine_handle = None
	n = len("from_archive")
	while True:
		inst = input_pipe.recv_bytes()
		if inst == b"shutdown":
			input_pipe.close()
			output_pipe.close()
			if log_queue:
				log_queue.close()
			return 0
		elif len(inst) > n and inst[:n] == b"from_archive":
			if engine_handle is not None:
				engine_handle.close()
			engine_handle = EngineHandle.from_archive(inst[n:])
			send_output("get_btt", engine_handle.get_btt())
			continue
		elif engine_handle is None:
			engine_handle = EngineHandle(*args, log_queue=log_queue, **kwargs)
			send_output("get_btt", engine_handle.get_btt())
			continue
		instruction = engine_handle.unpack(zlib.decompress(inst))
		_engine_subroutine_step(
			engine_handle, instruction, send_output, send_output_bytes
		)


def engine_subthread(args, kwargs, input_queue, output_queue):
	def send_output(cmd, r):
		output_queue.put((cmd, *engine_handle._real.time, r))

	def send_output_bytes(cmd, r):
		output_queue.put(
			engine_handle.unpack(
				_finish_packing(
					engine_handle.pack, cmd, *engine_handle._real.time, r
				)
			)
		)

	engine_handle = None

	while True:
		instruction = input_queue.get()
		if instruction == "shutdown" or instruction == b"shutdown":
			return
		if (
			isinstance(instruction, tuple)
			and instruction
			and instruction[0] == "from_archive"
		):
			engine_handle = EngineHandle.from_archive(instruction[1])
			send_output("get_btt", engine_handle.get_btt())
			continue
		if engine_handle is None:
			engine_handle = EngineHandle(*args, **kwargs)
			send_output("get_btt", engine_handle.get_btt())
			continue
		_engine_subroutine_step(
			engine_handle, instruction, send_output, send_output_bytes
		)


class WorkerLogHandler(logging.Handler):
	def __init__(self, logq, level, i):
		super().__init__(level)
		self._logq = logq
		self._i = i

	def emit(self, record):
		record.worker_idx = self._i
		self._logq.put(record)


def worker_subprocess(
	i: int,
	prefix: str,
	branches: dict,
	eternal: dict,
	in_pipe: "multiprocessing.Pipe",
	out_pipe: "multiprocessing.Pipe",
	logq: Queue,
	function: dict,
	method: dict,
	trigger: dict,
	prereq: dict,
	action: dict,
):
	logger = logging.getLogger(f"lisien worker {i}")
	handler = WorkerLogHandler(logq, logging.DEBUG, i)
	logger.addHandler(handler)
	eng = EngineProxy(
		None,
		None,
		logger,
		prefix=prefix,
		worker_index=i,
		eternal=eternal,
		branches=branches,
		function=function,
		method=method,
		trigger=trigger,
		prereq=prereq,
		action=action,
	)
	pack = eng.pack
	unpack = eng.unpack
	compress = zlib.compress
	decompress = zlib.decompress
	eng._initialized = False
	while True:
		inst = in_pipe.recv_bytes()
		if inst == b"shutdown":
			in_pipe.close()
			if logq and hasattr(logq, "close"):
				logq.close()
			out_pipe.send_bytes(b"done")
			out_pipe.close()
			sys.exit(0)
		uid = int.from_bytes(inst[:8], "little")
		(method, args, kwargs) = unpack(decompress(inst[8:]))
		if isinstance(method, str):
			method = getattr(eng, method)
		try:
			ret = method(*args, **kwargs)
		except Exception as ex:
			ret = ex
			if uid == sys.maxsize:
				msg = repr(ex)
				logq.put((50, msg))
				import traceback

				traceback.print_exc(file=sys.stderr)
				sys.exit(msg)
		if uid != sys.maxsize:
			out_pipe.send_bytes(inst[:8] + compress(pack(ret)))
		eng._initialized = True


class EngineProcessManager:
	"""Container for a Lisien proxy and a logger for it

	Make sure the :class:`EngineProcessManager` instance lasts as long as the
	:class:`lisien.proxy.EngineProxy` returned from its :method:`start`
	method. Call the :method:`EngineProcessManager.shutdown` method
	when you're done with the :class:`lisien.proxy.EngineProxy`. That way,
	we can join the thread that listens to the subprocess's logs.

	:param use_thread: Actually use a thread, not a process.

	"""

	loglevel = logging.DEBUG

	def __init__(
		self,
		*args,
		use_thread: bool = False,
		service_class_name: str = "org.tacmeta.elide.core",
		**kwargs,
	):
		self.use_thread = use_thread
		self.service_class_name = service_class_name
		self._args = args
		self._kwargs = kwargs

	def _config_logger(self, kwargs):
		handlers = []
		logl = {
			"debug": logging.DEBUG,
			"info": logging.INFO,
			"warning": logging.WARNING,
			"error": logging.ERROR,
			"critical": logging.CRITICAL,
		}
		loglevel = self.loglevel
		if "loglevel" in kwargs:
			if kwargs["loglevel"] in logl:
				loglevel = logl[kwargs["loglevel"]]
			else:
				loglevel = kwargs["loglevel"]
			del kwargs["loglevel"]
		if "logger" in kwargs:
			self.logger = kwargs["logger"]
		else:
			self.logger = logging.getLogger(__name__)
			stdout = logging.StreamHandler(sys.stdout)
			stdout.set_name("stdout")
			handlers.append(stdout)
			handlers[0].setLevel(loglevel)
		if "logfile" in kwargs:
			try:
				fh = logging.FileHandler(kwargs.pop("logfile"))
				handlers.append(fh)
				handlers[-1].setLevel(loglevel)
			except OSError:
				pass
		formatter = logging.Formatter(
			fmt="[{levelname}] lisien.proxy({process}) {message}", style="{"
		)
		for handler in handlers:
			handler.setFormatter(formatter)
			self.logger.addHandler(handler)

	def _start_subprocess(self, *args, **kwargs):
		try:
			import android
		except ImportError:
			if not hasattr(self, "use_thread"):
				from multiprocessing import Pipe, SimpleQueue

				(self._handle_in_pipe, self._proxy_out_pipe) = Pipe(
					duplex=False
				)
				(self._proxy_in_pipe, self._handle_out_pipe) = Pipe(
					duplex=False
				)
				self._logq = SimpleQueue()
		if hasattr(self, "_handle_in_pipe") and hasattr(
			self, "_handle_out_pipe"
		):
			from multiprocessing import Process

			self._p = Process(
				name="Lisien Life Simulator Engine (core)",
				target=engine_subprocess,
				args=(
					args or self._args,
					self._kwargs | kwargs,
					self._handle_in_pipe,
					self._handle_out_pipe,
				),
				kwargs={"log_queue": self._logq},
			)
			self._p.start()
		else:
			from queue import SimpleQueue

			self._input_queue = SimpleQueue()
			self._output_queue = SimpleQueue()

			self._t = Thread(
				target=engine_subthread,
				args=(
					args or self._args,
					self._kwargs | kwargs,
					self._input_queue,
					self._output_queue,
				),
			)
			self._t.start()

	def _make_proxy(self, *args, **kwargs):
		self._config_logger(kwargs)
		install_modules = (
			kwargs.pop("install_modules")
			if "install_modules" in kwargs
			else []
		)
		if not hasattr(self, "_t"):
			self._start_subprocess(*args, **kwargs)
		enforce_end_of_time = kwargs.get("enforce_end_of_time", False)
		if hasattr(self, "_handle_in_pipe") and hasattr(
			self, "_handle_out_pipe"
		):
			self.engine_proxy = EngineProxy(
				self._proxy_in_pipe,
				self._proxy_out_pipe,
				self.logger,
				install_modules,
				enforce_end_of_time=enforce_end_of_time,
			)
		else:
			self.engine_proxy = EngineProxy(
				self._input_queue,
				self._output_queue,
				self.logger,
				install_modules,
				enforce_end_of_time=enforce_end_of_time,
			)

		return self.engine_proxy

	def load_archive(
		self,
		archive_path: str | os.PathLike,
		prefix: str | os.PathLike,
		**kwargs,
	) -> EngineProxy:
		"""Load a game from a .lisien archive, start Lisien on it, and return its proxy"""
		n = len(".lisien")
		if archive_path[-n:] != ".lisien":
			raise RuntimeError("Not a .lisien archive")
		self._start_subprocess()
		self._config_logger(kwargs)
		if hasattr(self, "_proxy_in_pipe"):
			self._proxy_in_pipe.send(
				b"from_archive"
				+ msgpack.packb(
					{"archive_path": archive_path, "prefix": prefix, **kwargs}
				)
			)
		else:
			self._input_queue.put(
				(
					"from_archive",
					{"archive_path": archive_path, "prefix": prefix, **kwargs},
				)
			)
		self._make_proxy()
		self.engine_proxy._init_pull_from_core()
		return self.engine_proxy

	def start(self, *args, **kwargs) -> EngineProxy:
		"""Start lisien in a subprocess, and return a proxy to it"""
		if hasattr(self, "engine_proxy"):
			raise RuntimeError("Already started")
		self._config_logger(kwargs)
		self._make_proxy(*args, **kwargs)
		if hasattr(self, "_input_queue"):
			self._input_queue.put(b"")
		else:
			self._proxy_in_pipe.send(b"")
		self.engine_proxy._init_pull_from_core()
		return self.engine_proxy

	def _sync_log_forever(self):
		while True:
			logrec = self._logq.get()
			self.logger.handle(self._undictify_logrec_traceback(logrec))

	def _undictify_logrec_traceback(
		self, logrec: logging.LogRecord
	) -> logging.LogRecord:
		if logrec.exc_info:
			if isinstance(logrec.exc_info, Exception):
				logrec.exc_info.__traceback__ = tblib.Traceback.from_dict(
					logrec.exc_info.__traceback__
				).as_traceback()
			elif (
				isinstance(logrec.exc_info, tuple)
				and len(logrec.exc_info) == 3
				and logrec.exc_info[2]
			):
				logrec.exc_info = (
					logrec.exc_info[0],
					logrec.exc_info[1],
					tblib.Traceback.from_dict(
						logrec.exc_info[2]
					).as_traceback(),
				)
		return logrec

	def _handle_log_record(self, _, logrec_packed: bytes):
		self.logger.handle(
			self._undictify_logrec_traceback(pickle.loads(logrec_packed))
		)

	def log(self, level: str | int, msg: str):
		if isinstance(level, str):
			level = {
				"debug": 10,
				"info": 20,
				"warning": 30,
				"error": 40,
				"critical": 50,
			}[level.lower()]
		self.logger.log(level, msg)

	def shutdown(self):
		"""Close the engine in the subprocess, then join the subprocess"""
		if hasattr(self, "engine_proxy"):
			self.engine_proxy.close()
			if hasattr(self, "_p"):
				self.engine_proxy._pipe_out.send_bytes(b"shutdown")
				self._p.join()
			if hasattr(self, "_t"):
				self._input_queue.put("shutdown")
				self._t.join()
			del self.engine_proxy

	def __enter__(self):
		return self.start()

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.shutdown()
