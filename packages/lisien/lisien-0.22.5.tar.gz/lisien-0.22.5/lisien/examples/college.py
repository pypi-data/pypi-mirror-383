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
"""A simulation of students and teachers, both living on campus,
attending classes and teaching or learning, as appropriate.

Learning is modeled in a way similar to the game Kudos 2: each
student has 100 "brain cells," and the teacher sends an experience
point to each, once per lesson. If the brain cell is awake and
alert, the student receives the experience point and puts it toward
leveling-up. Otherwise it's wasted.

Some students are slow and some are drunkards. These students will
randomly show up late (brain cells become useless in proportion to
how late, recovering immediately afterward) or drunk (some brain
cells made useless per drink, recovering as time passes).

This is implemented inefficiently. I've been using it as a stress test.

"""


def two_way(orig, dest):
	orig.new_portal(dest.name)
	dest.new_portal(orig.name)


def install(eng):
	phys = eng.new_character("physical")
	phys.stat["hour"] = 0

	@phys.rule(always=True)  # runs every tick regardless of the situation
	def time_passes(character):
		character.stat["hour"] = (character.stat["hour"] + 1) % 24

	# There's a character with all of the students in it, to make it easy to apply rules to all students.
	student_body = eng.new_character("student_body")

	classroom = phys.new_place("classroom")

	@student_body.unit.rule
	def go_to_class(node):
		# There's just one really long class every day.
		node.travel_to(node.character.place["classroom"])

	@go_to_class.trigger
	def class_in_session(node):
		return 8 <= node.engine.character["physical"].stat["hour"] < 15

	@go_to_class.prereq
	def absent(node):
		assert hasattr(node, "location"), (
			f"Tried to get location of {node.name} in {node.character.name}"
		)
		return node.location != node.character.place["classroom"]

	@go_to_class.prereq
	def be_timely(node):
		# Even lazy students have a 50% chance of going to class every hour.
		#
		# We need to access the student character like this because the
		# ``character`` passed into the function is ``student_body``, where the
		# rule was assigned.
		#
		# Or we could have put the 'lazy' stat onto the node instead of the
		# character... or kept the student character in a stat of the node...
		# or assigned this rule to the student directly.
		for user in node.leader.values():
			if user.name not in ("physical", "student_body"):
				return not user.stat["lazy"] or node.engine.coin_flip()

	@student_body.unit.rule
	def leave_class(node):
		for user in node.leader.values():
			if user.name != "student_body":
				node.travel_to(user.stat["room"])
				return

	@leave_class.trigger
	def in_classroom_after_class(node):
		assert hasattr(node, "location"), (
			f"Tried to get location of {node.name} in {node.character.name}"
		)
		phys = node.character
		return (
			node.location == phys.place["classroom"]
			and phys.stat["hour"] >= 15
		)

	# Let's make some rules and not assign them to anything yet.
	@eng.rule
	def drink(character):
		braincells = list(character.node.values())
		character.engine.shuffle(braincells)
		for i in range(0, character.engine.randrange(1, 20)):
			braincells.pop()["drunk"] += 12

	@drink.trigger
	def party_time(character):
		phys = character.engine.character["physical"]
		return 23 >= phys.stat["hour"] > 15

	@drink.prereq
	def is_drunkard(character):
		return character.stat["drunkard"]

	@eng.rule
	def sloth(character):
		braincells = list(character.node.values())
		character.engine.shuffle(braincells)
		for i in range(0, character.engine.randrange(1, 20)):
			braincells.pop()["slow"] += 1

	@sloth.trigger
	def out_of_class(character):
		# You don't want to use the global variable for the classroom
		# because it won't be around (or at least, won't work) after
		# the engine restarts.
		unit = character.unit["physical"].only
		assert hasattr(unit, "location"), (
			f"Tried to get location of {unit.name} in physical, a unit of {character.name}"
		)
		classroom = unit.character.place["classroom"]
		return unit.location != classroom

	sloth.prereq(class_in_session)

	@eng.rule
	def learn(node):
		for user in node.leader.values():
			if "xp" in user.stat:
				user.stat["xp"] += 1

	@learn.trigger
	def in_class(node):
		classroom = node.engine.character["physical"].place["classroom"]
		student = node.character.unit["physical"].only
		assert hasattr(student, "location"), (
			f"Tried to get location of {student.name} in physical, a unit of {node.character.name}"
		)
		return student.location == classroom

	learn.prereq(class_in_session)
	learn.neighborhood = 0

	@learn.prereq
	def pay_attention(node):
		return node["drunk"] == node["slow"] == 0

	@eng.rule
	def sober_up(node):
		node["drunk"] -= 1

	@sober_up.trigger
	def somewhat_drunk(node):
		return node["drunk"] > 0

	@eng.rule
	def catch_up(node):
		node["slow"] -= 1

	@catch_up.trigger
	def somewhat_late(node):
		return node["slow"] > 0

	catch_up.prereq(in_class)
	catch_up.prereq(class_in_session)

	# 3 dorms of 12 students each.
	# Each dorm has 6 rooms.
	# Modeling the teachers would be a logical way to extend this.
	student_body.stat["characters"] = []
	for n in range(0, 3):
		dorm = eng.new_character("dorm{}".format(n))
		common = phys.new_place(
			"common{}".format(n)
		)  # A common room for students to meet in
		dorm.add_unit(common)
		two_way(common, classroom)
		# All rooms in a dorm are connected via its common room
		for i in range(0, 6):
			room = phys.new_place("dorm{}room{}".format(n, i))
			dorm.add_unit(room)
			two_way(room, common)
			student0 = eng.new_character("dorm{}room{}student0".format(n, i))
			body0 = room.new_thing("dorm{}room{}student0".format(n, i))
			student0.add_unit(body0)
			assert student0 in body0.leader.values()
			student_body.add_unit(body0)
			assert student_body in body0.leader.values()
			assert student0 in body0.leader.values()
			student1 = eng.new_character("dorm{}room{}student1".format(n, i))
			body1 = room.new_thing("dorm{}room{}student1".format(n, i))
			student1.add_unit(body1)
			student_body.add_unit(body1)
			student0.stat["room"] = student1.stat["room"] = room
			assert student0.stat["room"] == student1.stat["room"] == room
			student0.stat["roommate"] = student1
			student1.stat["roommate"] = student0
			for student in (student0, student1):
				if student not in student_body.stat["characters"]:
					student_body.stat["characters"].append(student)
				# Students' nodes are their brain cells.
				# They are useless if drunk or slow, but recover from both conditions a bit every hour.
				for k in range(0, 100):
					cell = student.new_node(
						"cell{}".format(k), drunk=0, slow=0
					)
					#  ``new_node`` is just an alias for ``new_place``;
					#  perhaps more logical when the places don't really
					#  represent potential locations
					student.stat["xp"] = 0
					student.stat["drunkard"] = eng.coin_flip()
					student.stat["lazy"] = eng.coin_flip()
				# Apply these previously written rules to each student
				for rule in (drink, sloth):
					student.rule(rule)
				# Apply these previously written rules to each brain cell
				for rule in (learn, sober_up, catch_up):
					student.place.rule(rule)
	eng.snap_keyframe()


if __name__ == "__main__":
	import sys

	from lisien.engine import Engine

	with Engine(sys.argv[-1]) as eng:
		install(eng)
