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
"""Wrap a lisien engine so you can access and control it using only
ordinary method calls.

"""

from __future__ import annotations

import os
from importlib import import_module
from logging import CRITICAL, DEBUG, ERROR, INFO, WARNING, Handler, Logger
from re import match
from typing import Any, Callable, Iterable, Optional

import msgpack
import networkx as nx
import tblib

from ..exc import HistoricKeyError, OutOfTimelineError
from ..node import Node
from ..portal import Portal
from ..types import (
	ActionFuncName,
	Branch,
	CharDelta,
	CharName,
	DeltaDict,
	EdgesDict,
	EdgeValDict,
	EternalKey,
	FuncName,
	FuncStoreName,
	Key,
	Keyframe,
	LinearTime,
	NodeName,
	NodeValDict,
	Plan,
	PrereqFuncName,
	RulebookName,
	RulebookPriority,
	RuleName,
	RuleNeighborhood,
	Stat,
	StatDict,
	Tick,
	Time,
	TriggerFuncName,
	Turn,
	UnitsDict,
	Value,
)
from ..util import (
	EDGE_VAL,
	EDGES,
	ELLIPSIS,
	EMPTY_MAPPING,
	ETERNAL,
	NODE_VAL,
	NODES,
	NONE,
	RULEBOOK,
	RULEBOOKS,
	RULES,
	UNITS,
	UNIVERSAL,
	AbstractCharacter,
	BadTimeException,
	timer,
)

SlightlyPackedDeltaType = dict[
	bytes,
	dict[
		bytes,
		bytes | dict[bytes, bytes | dict[bytes, bytes | dict[bytes, bytes]]],
	],
]
FormerAndCurrentType = tuple[dict[bytes, bytes], dict[bytes, bytes]]


def concat_d(r: dict[bytes, bytes]) -> bytes:
	"""Pack a dictionary of msgpack-encoded keys and values into msgpack bytes"""
	resp = msgpack.Packer().pack_map_header(len(r))
	for k, v in r.items():
		resp += k + v
	return resp


def prepacked(fun: Callable) -> Callable:
	fun.prepacked = True
	return fun


class EngineHandleLogHandler(Handler):
	def __init__(self, level: int, log_queue):
		super().__init__(level)
		self._logq = log_queue

	def emit(self, record):
		if record.exc_info:
			if (
				isinstance(record.exc_info, Exception)
				and record.exc_info.__traceback__
			):
				record.exc_info.__traceback__ = tblib.Traceback(
					record.exc_info.__traceback__
				).as_dict()
			elif (
				isinstance(record.exc_info, tuple)
				and len(record.exc_info) == 3
				and record.exc_info[2]
			):
				record.exc_info = (
					record.exc_info[0],
					record.exc_info[1],
					tblib.Traceback(record.exc_info[2]).as_dict(),
				)
		self._logq.put(record)


class EngineHandle:
	"""A wrapper for a :class:`lisien.Engine` object that runs in the same
	process, but with an API built to be used in a command-processing
	loop that takes commands from another process.

	It's probably a bad idea to use this class unless you're
	developing your own API.

	"""

	_after_ret: Callable

	def __init__(self, *args, log_queue=None, **kwargs):
		"""Instantiate an engine with the given arguments"""
		from ..engine import Engine

		do_game_start = kwargs.pop("do_game_start", False)
		if log_queue:
			logger = kwargs["logger"] = Logger("lisien")
			handler = EngineHandleLogHandler(0, log_queue)
			logger.addHandler(handler)
		self._real = Engine(*args, **kwargs)
		self.pack = pack = self._real.pack

		def pack_pair(pair):
			k, v = pair
			return pack(k), pack(v)

		self.pack_pair = pack_pair
		self.unpack = self._real.unpack

		if do_game_start:
			self.do_game_start()

	@classmethod
	def from_archive(cls, b: bytes | dict) -> EngineHandle:
		from ..engine import Engine

		if isinstance(b, bytes):
			kwargs: dict = msgpack.unpackb(b)
		else:
			kwargs = b
		if "archive_path" not in kwargs:
			raise TypeError("No archive path")
		if "prefix" not in kwargs:
			raise TypeError("No prefix")
		do_game_start = kwargs.pop("do_game_start")

		new = cls.__new__(cls)
		new._real = Engine.from_archive(
			kwargs.pop("archive_path"), kwargs.pop("prefix"), **kwargs
		)
		new.pack = pack = new._real.pack

		def pack_pair(pair):
			k, v = pair
			return pack(k), pack(v)

		new.pack_pair = pack_pair
		new.unpack = new._real.unpack
		if do_game_start:
			new.do_game_start()
		return new

	def export(self, name: str | None, path: str | None):
		return self._real.export(name, path)

	def log(self, level: str | int, message: str) -> None:
		if isinstance(level, str):
			level = {
				"debug": 10,
				"info": 20,
				"warning": 30,
				"error": 40,
				"critical": 50,
			}[level.lower()]
		self._real.logger.log(level, message)

	def debug(self, message: str) -> None:
		self.log(DEBUG, message)

	def info(self, message: str) -> None:
		self.log(INFO, message)

	def warning(self, message: str) -> None:
		self.log(WARNING, message)

	def error(self, message: str) -> None:
		self.log(ERROR, message)

	def critical(self, message: str) -> None:
		self.log(CRITICAL, message)

	def time_locked(self) -> bool:
		"""Return whether the sim-time has been prevented from advancing"""
		return hasattr(self._real, "locktime")

	def snap_keyframe(self, silent: bool = False) -> Keyframe:
		return self._real.snap_keyframe(silent=silent)

	def _pack_delta(
		self, delta: DeltaDict
	) -> tuple[SlightlyPackedDeltaType, bytes]:
		pack = self.pack
		slightly_packed_delta = {}
		mostly_packed_delta = {}
		for char, chardelta in delta.items():
			if chardelta is ...:
				pchar = pack(char)
				slightly_packed_delta[pchar] = mostly_packed_delta[pchar] = (
					None
				)
				continue
			chardelta = chardelta.copy()
			pchar = pack(char)
			chard = slightly_packed_delta[pchar] = {}
			packd = mostly_packed_delta[pchar] = {}
			if "nodes" in chardelta:
				nd = chard[NODES] = {
					pack(node): pack(ex)
					for node, ex in chardelta.pop("nodes").items()
				}
				packd[NODES] = concat_d(nd)
			if "node_val" in chardelta:
				slightnoded = chard[NODE_VAL] = {}
				packnodevd = {}
				nodedelta: NodeValDict = chardelta.pop("node_val")
				for node, vals in nodedelta.items():
					pnode = pack(node)
					pvals = dict(map(self.pack_pair, vals.items()))
					slightnoded[pnode] = pvals
					packnodevd[pnode] = concat_d(pvals)
				packd[NODE_VAL] = concat_d(packnodevd)
			if "edges" in chardelta:
				edgedelta: EdgesDict = chardelta.pop("edges")
				ed = chard[EDGES] = {
					pack(origdest): pack(ex)
					for origdest, ex in edgedelta.items()
				}
				packd[EDGES] = concat_d(ed)
			if "edge_val" in chardelta:
				slightorigd = chard[EDGE_VAL] = {}
				packorigd = {}
				edgevaldelta: EdgeValDict = chardelta.pop("edge_val")
				for orig, dests in edgevaldelta.items():
					porig = pack(orig)
					slightdestd = slightorigd[porig] = {}
					packdestd = {}
					for dest, port in dests.items():
						pdest = pack(dest)
						slightportd = slightdestd[pdest] = dict(
							map(self.pack_pair, port.items())
						)
						packdestd[pdest] = concat_d(slightportd)
					packorigd[porig] = concat_d(packdestd)
				packd[EDGE_VAL] = concat_d(packorigd)
			if "units" in chardelta:
				slightgraphd = chard[UNITS] = {}
				packunitd = {}
				unitdelta: UnitsDict = chardelta.pop("units")
				for graph, unitss in unitdelta.items():
					if unitss is None:
						continue
					pgraph = pack(graph)
					slightunitd = slightgraphd[pgraph] = dict(
						map(self.pack_pair, unitss.items())
					)
					packunitd[pgraph] = concat_d(slightunitd)
				packd[UNITS] = concat_d(packunitd)
			if "rulebooks" in chardelta:
				chard[RULEBOOKS] = slightrbd = dict(
					map(self.pack_pair, chardelta.pop("rulebooks").items())
				)
				packd[RULEBOOKS] = concat_d(slightrbd)
			todo = dict(map(self.pack_pair, chardelta.items()))
			chard.update(todo)
			packd.update(todo)
		return slightly_packed_delta, concat_d(
			{
				charn: (concat_d(stuff) if stuff is not None else NONE)
				for charn, stuff in mostly_packed_delta.items()
			}
		)

	@staticmethod
	def _concat_char_delta(delta: SlightlyPackedDeltaType) -> bytes:
		delta = delta.copy()
		mostly_packed_delta = packd = {}
		eternal = delta.pop(ETERNAL, None)
		if eternal:
			mostly_packed_delta[ETERNAL] = eternal
		universal = delta.pop(UNIVERSAL, None)
		if universal:
			mostly_packed_delta[UNIVERSAL] = universal
		if RULEBOOK in delta:
			mostly_packed_delta[RULEBOOK] = delta.pop(RULEBOOK)
		if RULES in delta:
			rules = delta.pop(RULES)
			mostly_packed_delta[RULES] = concat_d(
				{rule: concat_d(funcls) for (rule, funcls) in rules.items()}
			)
		if NODES in delta:
			charnodes = delta.pop(NODES)
			packd[NODES] = concat_d(charnodes)
		if NODE_VAL in delta:
			slightnoded = {}
			packnodevd = {}
			for node, vals in delta.pop(NODE_VAL).items():
				slightnoded[node] = vals
				packnodevd[node] = concat_d(vals)
			packd[NODE_VAL] = concat_d(packnodevd)
		if EDGES in delta:
			es = delta.pop(EDGES)
			packd[EDGES] = concat_d(es)
		if EDGE_VAL in delta:
			packorigd = {}
			for orig, dests in delta.pop(EDGE_VAL).items():
				slightdestd = {}
				packdestd = {}
				for dest, port in dests.items():
					slightdestd[dest] = port
					packdestd[dest] = concat_d(port)
				packorigd[orig] = concat_d(packdestd)
			packd[EDGE_VAL] = concat_d(packorigd)
		if UNITS in delta:
			if delta[UNITS] == NONE:
				packd[UNITS] = concat_d({})
				del delta[UNITS]
			else:
				packd[UNITS] = delta.pop(UNITS)
		mostly_packed_delta.update(delta)
		return concat_d(mostly_packed_delta)

	@prepacked
	def next_turn(self) -> tuple[bytes, bytes]:
		"""Simulate a turn. Return whatever result, as well as a delta"""
		pack = self.pack
		self.debug(
			"calling next_turn at {}, {}, {}".format(*self._real._btt())
		)
		ret, delta = self._real.next_turn()
		slightly_packed_delta, packed_delta = self._pack_delta(delta)
		return pack(ret), packed_delta

	def _get_slow_delta(
		self,
		btt_from: Time | None = None,
		btt_to: Time | None = None,
	) -> SlightlyPackedDeltaType:
		return self._real._get_slow_delta(btt_from, btt_to)

	def bookmarks_dump(self) -> list[tuple[Key, Time]]:
		return list(self._real.query.bookmark_items())

	def set_bookmark(self, key: Key, time: Time | None = None) -> Time:
		if time is None:
			self._real.bookmark(key)
			return tuple(self._real.time)
		else:
			self._real.bookmark[key] = time
			return time

	def del_bookmark(self, key: Key):
		del self._real.bookmark[key]

	def start_branch(
		self, parent: Branch, branch: Branch, turn: Turn, tick: Tick
	):
		self._real._start_branch(parent, branch, turn, tick)

	def extend_branch(self, branch: Branch, turn: Turn, tick: Tick):
		self._real._extend_branch(branch, turn, tick)

	def load_at(self, branch: Branch, turn: Turn, tick: Tick):
		self._real.load_at(branch, turn, tick)

	def turn_end(
		self, branch: Branch | None = None, turn: Turn | None = None
	) -> Tick:
		return self._real.turn_end(branch, turn)

	def turn_end_plan(
		self, branch: Branch | None = None, turn: Turn | None = None
	) -> Tick:
		return self._real.turn_end_plan(branch, turn)

	def branch_end(self, branch: Optional[Branch] = None) -> Turn:
		return self._real.branch_end(branch)

	def branch_end_turn_and_tick(self, branch: Branch) -> LinearTime:
		branch = Branch(branch)
		turn = self._real.branch_end_turn(branch)
		return turn, self._real.turn_end(branch, turn)

	def branch_end_plan_turn_and_tick(self, branch: Branch) -> LinearTime:
		branch = Branch(branch)
		turn = self._real.branch_end_turn(branch)
		return turn, self._real.turn_end_plan(branch, turn)

	def start_plan(self) -> Plan:
		self._plan_ctx = self._real.plan()
		return self._plan_ctx.__enter__()

	def end_plan(self) -> tuple[None, DeltaDict]:
		time_was = self._real._btt()
		self._plan_ctx.__exit__(None, None, None)
		del self._plan_ctx
		return None, self._real.get_delta(time_was, self._real._btt())

	@prepacked
	def time_travel(
		self,
		branch: Branch,
		turn: Turn,
		tick: Tick | None = None,
	) -> tuple[bytes, bytes]:
		"""Go to a different `(branch, turn, tick)` and return a delta

		For compatibility with `next_turn` this actually returns a tuple,
		the 0th item of which is `None`.

		"""
		if branch in self._real.branches():
			if self._real._enforce_end_of_time:
				turn_end, tick_end = self._real._branch_end(branch)
				if (tick is None and turn > turn_end) or (
					tick is not None and (turn, tick) > (turn_end, tick_end)
				):
					raise OutOfTimelineError(
						"Not traveling past the end of the branch",
						branch,
						turn,
						tick,
						turn_end,
						tick_end,
					)
			self._real.load_at(branch, turn, tick)
		branch_from, turn_from, tick_from = self._real._btt()
		if tick is None:
			if (
				branch,
				turn,
				self._real.turn_end(branch, turn),
			) == (
				branch_from,
				turn_from,
				tick_from,
			):
				return NONE, EMPTY_MAPPING
			self._real.time = (branch, turn, self._real.turn_end(branch, turn))
		else:
			if (branch, turn, tick) == (
				branch_from,
				turn_from,
				tick_from,
			):
				return NONE, EMPTY_MAPPING
			self._real.time = (branch, turn, tick)
		if turn_from != turn and (
			branch_from != branch
			or None in (turn_from, turn)
			or self._real._is_timespan_too_big(branch, turn_from, turn)
		):
			# This branch avoids unpacking and re-packing the delta
			slightly: SlightlyPackedDeltaType = self._real._get_slow_delta(
				(branch_from, turn_from, tick_from), self._real._btt()
			)
			mostly = {}
			if UNIVERSAL in slightly:
				mostly[UNIVERSAL] = concat_d(slightly.pop(UNIVERSAL))
			if RULES in slightly:
				mostly[RULES] = concat_d(
					{
						rule: concat_d(rule_d)
						for (rule, rule_d) in slightly.pop(RULES).items()
					}
				)
			if RULEBOOK in slightly:
				mostly[RULEBOOK] = concat_d(slightly.pop(RULEBOOK))
			for char, chardeltapacked in slightly.items():
				if chardeltapacked == ELLIPSIS:
					mostly[char] = ELLIPSIS
					continue
				mostly[char] = self._concat_char_delta(chardeltapacked)
			return NONE, concat_d(mostly)
		return NONE, self._pack_delta(
			self._real.get_delta(
				(branch_from, turn_from, tick_from), self._real._btt()
			)
		)[1]

	@prepacked
	def increment_branch(self) -> bytes:
		"""Generate a new branch name and switch to it

		Returns the name of the new branch.

		"""
		branch = self._real.branch
		m = match(r"(.*)(\d+)", branch)
		if m:
			stem, n = m.groups()
			branch = stem + str(int(n) + 1)
		else:
			stem = branch
			n = 1
			branch = stem + str(n)
		if branch in self._real.branches():
			if m:
				n = int(n)
			else:
				stem = branch[:-1]
				n = 1
			while stem + str(n) in self._real.branches():
				n += 1
			branch = stem + str(n)
		self._real.branch = branch
		return self.pack(branch)

	def add_character(
		self,
		char: CharName,
		data: nx.Graph | nx.DiGraph | None = None,
		node: NodeValDict | None = None,
		edge: EdgeValDict | None = None,
		**attr,
	):
		"""Make a new character, initialized with whatever data"""
		# Probably not great that I am unpacking and then repacking the stats
		self._real.add_character(char, data=data, node=node, edge=edge, **attr)

	def commit(self):
		self._real.commit()

	def close(self):
		self._real.close()

	def get_btt(self) -> Time:
		return self._real._btt()

	def get_language(self) -> str:
		return str(self._real.string.language)

	def set_language(self, lang: str) -> dict[str, str]:
		self._real.string.language = lang
		return self.strings_copy(lang)

	def get_string_lang_items(
		self, lang: str | None = None
	) -> list[tuple[str, str]]:
		return list(self._real.string.lang_items(lang))

	def strings_copy(self, lang: str | None = None) -> dict[str, str]:
		return dict(self._real.string.lang_items(lang))

	def set_string(self, k: str, v: str) -> None:
		self._real.string[k] = v

	def del_string(self, k: str) -> None:
		del self._real.string[k]

	@prepacked
	def get_eternal(self, k: EternalKey) -> bytes:
		return self.pack(self._real.eternal[k])

	def set_eternal(self, k: EternalKey, v: Value) -> None:
		self._real.eternal[k] = v

	def del_eternal(self, k: EternalKey) -> None:
		del self._real.eternal[k]

	@prepacked
	def eternal_copy(self) -> dict[bytes, bytes]:
		return dict(map(self.pack_pair, self._real.eternal.items()))

	def set_universal(self, k: EternalKey, v: Value) -> None:
		self._real.universal[k] = v

	def del_universal(self, k: EternalKey) -> None:
		del self._real.universal[k]

	def del_character(self, char: CharName) -> None:
		del self._real.character[char]

	def set_character(self, char: CharName, data: CharDelta) -> None:
		self._real.character[char] = data

	def set_character_stat(self, char: CharName, k: Stat, v: Value) -> None:
		self._real.character[char].stat[k] = v

	def del_character_stat(self, char: CharName, k: Stat) -> None:
		del self._real.character[char].stat[k]

	def set_node_stat(
		self, char: CharName, node: NodeName, k: Stat, v: Value
	) -> None:
		self._real.character[char].node[node][k] = v

	def del_node_stat(self, char: CharName, node: NodeName, k: Stat) -> None:
		del self._real.character[char].node[node][k]

	def _get_btt(self, btt: Time | None = None) -> Time:
		if btt is None:
			return self._real._btt()
		return btt

	def node_exists(self, char: CharName, node: NodeName) -> bool:
		return self._real._node_exists(char, node)

	def update_nodes(self, char: CharName, patch: NodeValDict):
		"""Change the stats of nodes in a character according to a
		dictionary.

		"""
		node = self._real.character[char].node
		with (
			self._real.batch(),
			timer("EngineHandle.update_nodes", self.debug),
		):
			for n, npatch in patch.items():
				if npatch is None:
					del node[n]
				elif n not in node:
					node[n] = npatch
				else:
					node[n].update(npatch)

	def del_node(self, char: CharName, node: NodeName):
		"""Remove a node from a character."""
		del self._real.character[char].node[node]

	def character_set_node_predecessors(
		self, char: CharName, node: NodeName, preds: Iterable
	) -> None:
		self._real.character[char].pred[node] = preds

	def set_thing(
		self, char: CharName, thing: NodeName, statdict: dict
	) -> None:
		self._real.character[char].thing[thing] = statdict

	def add_thing(
		self, char: CharName, thing: NodeName, loc: NodeName, statdict: dict
	) -> None:
		self._real.character[char].add_thing(thing, loc, **statdict)

	def place2thing(self, char: CharName, place: NodeName, loc: NodeName):
		self._real.character[char].place2thing(place, loc)

	def thing2place(self, char: CharName, thing: NodeName):
		self._real.character[char].thing2place(thing)

	def set_thing_location(
		self, char: CharName, thing: NodeName, loc: NodeName
	) -> None:
		self._real.character[char].thing[thing]["location"] = loc

	def thing_follow_path(
		self,
		char: CharName,
		thing: NodeName,
		path: list[NodeName],
		weight: Stat,
	) -> int:
		return (
			self._real.character[char].thing[thing].follow_path(path, weight)
		)

	def thing_go_to_place(
		self, char: CharName, thing: NodeName, place: NodeName, weight: Stat
	) -> int:
		return (
			self._real.character[char].thing[thing].go_to_place(place, weight)
		)

	def thing_travel_to(
		self,
		char: CharName,
		thing: NodeName,
		dest: NodeName,
		weight: Stat | None = None,
		graph: nx.DiGraph | None = None,
	) -> int:
		"""Make something find a path to ``dest`` and follow it.

		Optional argument ``weight`` is the portal stat to use to schedule
		movement times.

		Optional argument ``graph`` is an alternative graph to use for
		pathfinding. Should resemble a networkx DiGraph.

		"""
		return (
			self._real.character[char]
			.thing[thing]
			.travel_to(dest, weight, graph)
		)

	def set_place(
		self, char: CharName, place: NodeName, statdict: StatDict
	) -> None:
		self._real.character[char].place[place] = statdict

	def add_places_from(self, char: CharName, seq: Iterable) -> None:
		self._real.character[char].add_places_from(seq)

	def add_portal(
		self,
		char: CharName,
		orig: NodeName,
		dest: NodeName,
		statdict: StatDict,
		symmetrical: bool = False,
	) -> None:
		self._real.character[char].add_portal(orig, dest, **statdict)
		if symmetrical:
			self._real.character[char].add_portal(dest, orig, **statdict)

	def add_portals_from(self, char: CharName, seq: Iterable) -> None:
		self._real.character[char].add_portals_from(seq)

	def del_portal(
		self, char: CharName, orig: NodeName, dest: NodeName
	) -> None:
		ch = self._real.character[char]
		ch.remove_edge(orig, dest)
		assert orig in ch.node
		assert dest in ch.node

	def set_portal(
		self, char: CharName, orig: NodeName, dest: NodeName, v: StatDict
	):
		self._real.character[CharName(char)].portal[NodeName(orig)][
			NodeName(dest)
		] = v

	def set_portal_stat(
		self, char: CharName, orig: NodeName, dest: NodeName, k: Stat, v: Value
	) -> None:
		self._real.character[char].portal[orig][dest][k] = v

	def del_portal_stat(
		self, char: CharName, orig: NodeName, dest: NodeName, k: Stat
	) -> None:
		del self._real.character[char][orig][dest][k]

	def add_unit(
		self, char: CharName, graph: CharName, node: NodeName
	) -> None:
		self._real.character[char].add_unit(graph, node)

	def remove_unit(
		self, char: CharName, graph: CharName, node: NodeName
	) -> None:
		self._real.character[char].remove_unit(graph, node)

	def new_empty_rule(self, rule: RuleName) -> None:
		self._real.rule.new_empty(rule)

	def new_empty_rulebook(self, rulebook: RulebookName) -> list:
		self._real.rulebook.__getitem__(rulebook)
		return []

	def set_rulebook_priority(
		self, rulebook: RulebookName, priority: RulebookPriority
	) -> None:
		self._real.rulebook[rulebook].priority = priority

	def set_rulebook_rules(
		self, rulebook: RulebookName, rules: list[RuleName]
	) -> None:
		self._real.rulebook[rulebook] = rules

	def set_rulebook_rule(
		self, rulebook: RulebookName, i: int, rule: RuleName
	) -> None:
		self._real.rulebook[rulebook][i] = rule

	def ins_rulebook_rule(
		self, rulebook: RulebookName, i: int, rule: RuleName
	) -> None:
		self._real.rulebook[rulebook].insert(i, rule)

	def del_rulebook_rule(self, rulebook: RulebookName, i: int) -> None:
		del self._real.rulebook[rulebook][i]

	def move_rulebook_rule_back(self, rulebook: RulebookName, i: int) -> int:
		rb = self._real.rulebook[rulebook]
		rule = rb.pop(i)
		rb.insert(i - 1, rule)
		return i - 1

	def move_rulebook_rule_forward(
		self, rulebook: RulebookName, i: int
	) -> int:
		rb = self._real.rulebook[rulebook]
		rule = rb.pop(i)
		rb.insert(i + 1, rule)
		return i + 1

	def del_rulebook(self, rulebook: RulebookName) -> None:
		del self._real.rulebook[rulebook]

	def del_rule(self, rule: RuleName) -> None:
		del self._real.rule[rule]

	def set_rule_triggers(
		self, rule: RuleName, triggers: list[TriggerFuncName]
	) -> None:
		self._real.rule[rule].triggers = triggers

	def set_rule_prereqs(
		self, rule: RuleName, prereqs: list[PrereqFuncName]
	) -> None:
		self._real.rule[rule].prereqs = prereqs

	def set_rule_actions(
		self, rule: RuleName, actions: list[ActionFuncName]
	) -> None:
		self._real.rule[rule].actions = actions

	def set_rule_neighborhood(
		self, rule: RuleName, neighborhood: RuleNeighborhood
	) -> None:
		self._real.rule[rule].neighborhood = neighborhood

	def get_rule_neighborhood(self, rule: RuleName) -> RuleNeighborhood:
		return self._real.rule[rule].neighborhood

	def set_character_rulebook(
		self, char: CharName, rulebook: RulebookName
	) -> None:
		self._real.character[char].rulebook = rulebook

	def set_unit_rulebook(
		self, char: CharName, rulebook: RulebookName
	) -> None:
		self._real.character[char].unit.rulebook = rulebook

	def set_character_thing_rulebook(
		self, char: CharName, rulebook: RulebookName
	) -> None:
		self._real.character[char].thing.rulebook = rulebook

	def set_character_place_rulebook(
		self, char: CharName, rulebook: RulebookName
	) -> None:
		self._real.character[char].place.rulebook = rulebook

	def set_character_node_rulebook(
		self, char: CharName, rulebook: RulebookName
	) -> None:
		self._real.character[char].node.rulebook = rulebook

	def set_character_portal_rulebook(
		self, char: CharName, rulebook: RulebookName
	) -> None:
		self._real.character[char].portal.rulebook = rulebook

	def set_node_rulebook(
		self, char: CharName, node: NodeName, rulebook: RulebookName
	) -> None:
		self._real.character[char].node[node].rulebook = rulebook

	def set_portal_rulebook(
		self,
		char: CharName,
		orig: NodeName,
		dest: NodeName,
		rulebook: RulebookName,
	) -> None:
		self._real.character[char].portal[orig][dest].rulebook = rulebook

	@prepacked
	def source_copy(
		self,
		store: FuncStoreName,
	) -> dict[bytes, bytes]:
		return dict(
			map(self.pack_pair, getattr(self._real, store).iterplain())
		)

	def get_source(self, store: FuncStoreName, name: FuncName) -> str:
		return getattr(self._real, store).get_source(name)

	def store_source(
		self, store: FuncStoreName, v: str, name: FuncName | None = None
	) -> None:
		getattr(self._real, store).store_source(v, name)

	def del_source(self, store: FuncStoreName, k: FuncName) -> None:
		delattr(getattr(self._real, store), k)

	def call_stored_function(
		self, store: FuncStoreName, func: FuncName, args: tuple, kwargs: dict
	) -> Any:
		branch, turn, tick = self._real._btt()
		if store == "method":
			args = (self._real,) + tuple(args)
		store = getattr(self._real, store)
		if store not in self._real.stores:
			raise ValueError("{} is not a function store".format(store))
		callme = getattr(store, func)
		res = callme(*args, **kwargs)
		_, turn_now, tick_now = self._real._btt()
		delta = self._real._get_branch_delta(
			branch, turn, tick, turn_now, tick_now
		)
		return res, delta

	def call_randomizer(self, method: str, *args, **kwargs) -> Any:
		return getattr(self._real._rando, method)(*args, **kwargs)

	def install_module(self, module: str) -> None:
		import_module(module).install(self._real)

	def do_game_start(self):
		branch, turn, tick = self._real._btt()
		self._real.game_start()
		return [], self._real._get_branch_delta(
			branch, turn, tick, self._real.turn, self._real.tick
		)

	def is_ancestor_of(self, parent: Branch, child: Branch) -> bool:
		return self._real.is_ancestor_of(parent, child)

	def branch_start(self, branch: Branch) -> LinearTime:
		return self._real._branch_start(branch)

	def branch_parent(self, branch: Branch) -> str | None:
		return self._real.branch_parent(branch)

	def apply_choices(
		self,
		choices: list[dict],
		dry_run: bool = False,
		perfectionist: bool = False,
	) -> tuple[list[tuple[Any, Any]], list[tuple[Any, Any]]]:
		return self._real.apply_choices(choices, dry_run, perfectionist)

	@staticmethod
	def get_schedule(
		entity: AbstractCharacter | Node | Portal,
		stats: Iterable[Key],
		beginning: int,
		end: int,
	) -> dict[Key, list]:
		ret = {}
		for stat in stats:
			ret[stat] = list(
				entity.historical(stat).iter_history(beginning, end)
			)
		return ret

	def rules_handled_turn(
		self, branch: Branch | None = None, turn: Turn | None = None
	) -> dict[str, dict[int, dict[int, str]]]:
		if branch is None:
			branch = self._real.branch
		if turn is None:
			turn = self._real.turn
		eng = self._real
		# assume the caches are all sync'd
		try:
			return {
				"character": eng._character_rules_handled_cache.handled_deep[
					branch
				][turn],
				"unit": eng._unit_rules_handled_cache.handled_deep[branch][
					turn
				],
				"character_thing": eng._character_thing_rules_handled_cache.handled_deep[
					branch
				][turn],
				"character_place": eng._character_place_rules_handled_cache.handled_deep[
					branch
				][turn],
				"character_portal": eng._character_portal_rules_handled_cache.handled_deep[
					branch
				][turn],
				"node": eng._node_rules_handled_cache.handled_deep[branch][
					turn
				],
				"portal": eng._portal_rules_handled_cache.handled_deep[branch][
					turn
				],
			}
		except HistoricKeyError:
			return {
				"character": {},
				"unit": {},
				"character_thing": {},
				"character_place": {},
				"character_portal": {},
				"node": {},
				"portal": {},
			}

	def branches(
		self,
	) -> dict[Branch, tuple[Branch | None, Turn, Tick, Turn, Tick]]:
		return dict(self._real._branches_d)

	def main_branch(self) -> Branch:
		return self._real.trunk

	def switch_main_branch(self, branch: Branch) -> Keyframe:
		self._real.trunk = branch
		return self.snap_keyframe()

	def game_init(
		self,
	) -> tuple[
		Keyframe,
		dict[EternalKey, Value],
		dict[FuncName, str],
		dict[FuncName, str],
		dict[TriggerFuncName, str],
		dict[PrereqFuncName, str],
		dict[ActionFuncName, str],
	]:
		branch, turn, tick = self._real._btt()
		if (turn, tick) != (0, 0):
			raise BadTimeException(
				"You tried to start a game when it wasn't the start of time"
			)
		self.do_game_start()
		kf = self.snap_keyframe()
		functions = dict(self._real.function.iterplain())
		methods = dict(self._real.method.iterplain())
		triggers = dict(self._real.trigger.iterplain())
		prereqs = dict(self._real.prereq.iterplain())
		actions = dict(self._real.action.iterplain())
		return (
			kf,
			self._real.eternal.copy(),
			functions,
			methods,
			triggers,
			prereqs,
			actions,
		)


def serial_handle(prefix, **kwargs):
	kwargs["workers"] = 0
	return EngineHandle(prefix, **kwargs)
