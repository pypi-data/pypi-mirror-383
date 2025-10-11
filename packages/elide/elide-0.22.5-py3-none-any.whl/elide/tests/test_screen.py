import os
from functools import partial

import pytest
from kivy.base import EventLoop
from kivy.tests.common import UnitTestTouch

from lisien import Engine

from .util import idle_until


class MockStore:
	def save(self, *args):
		pass


@pytest.fixture(autouse=True)
def screen_test_state(prefix):
	with Engine(os.path.join(prefix, "test"), workers=0) as eng:
		foo = eng.new_character("physical")
		here = foo.new_place((0, 0))
		foo.add_place((1, 1))
		foo.add_place(9)  # test that gridboard can handle this
		this = here.new_thing(2)

		@this.rule(always=True)
		def go(me):
			if me["location"] == (1, 1):
				me["location"] = 9
			elif me["location"] == 9:
				me["location"] = (0, 0)
			else:
				me["location"] = (1, 1)


def test_advance_time(screen_test_state, elide_app):
	app = elide_app
	screen = app.mainscreen
	idle_until(
		lambda: "timepanel" in screen.ids, 100, "timepanel never got id"
	)
	timepanel = screen.ids["timepanel"]
	idle_until(
		lambda: timepanel.size != [100, 100],
		100,
		"timepanel never resized",
	)
	turnfield = timepanel.ids["turnfield"]
	turn_before = int(turnfield.hint_text)
	stepbut = timepanel.ids["stepbut"]
	motion = UnitTestTouch(*stepbut.center)
	motion.touch_down()
	motion.touch_up()
	idle_until(
		lambda: int(turnfield.hint_text) == turn_before + 1,
		100,
		"Never updated hint text",
	)


def test_play(screen_test_state, elide_app):
	app = elide_app
	screen = app.mainscreen
	idle_until(
		lambda: "timepanel" in screen.ids, 100, "timepanel never got id"
	)
	timepanel = screen.ids["timepanel"]
	idle_until(
		lambda: timepanel.size != [100, 100],
		100,
		"timepanel never resized",
	)
	turnfield = timepanel.ids["turnfield"]
	playbut = screen.playbut = timepanel.ids["playbut"]
	idle_until(lambda: screen.boardview, 100, "screen never got boardview")
	motion = UnitTestTouch(*playbut.center)
	motion.touch_down()
	motion.touch_up()
	idle_until(
		lambda: int(turnfield.hint_text) == 3,
		400,
		"Time didn't advance fast enough",
	)
	playbut.state = "normal"


def test_update(screen_test_state, elide_app):
	def almost(a, b):
		if isinstance(a, tuple) and isinstance(b, tuple):
			return all(almost(aa, bb) for (aa, bb) in zip(a, b))
		return abs(a - b) < 1

	app = elide_app
	idle_until(lambda: hasattr(app, "engine"), 100, "Never got engine proxy")
	assert app.engine.character["physical"].thing[2]["location"] == (0, 0)
	graphboard = app.mainscreen.graphboards["physical"]
	gridboard = app.mainscreen.gridboards["physical"]
	idle_until(
		lambda: graphboard.size != [100, 100],
		100,
		"Never resized graphboard",
	)
	idle_until(
		lambda: gridboard.size != [100, 100],
		100,
		"Never resized gridboard",
	)
	idle_until(
		lambda: (0, 0) in graphboard.spot,
		100,
		"Never made spot for location 0",
	)
	idle_until(
		lambda: 2 in graphboard.pawn, 100, "Never made pawn for thing 2"
	)
	locspot0 = graphboard.spot[0, 0]
	gridspot0 = gridboard.spot[0, 0]
	locspot1 = graphboard.spot[1, 1]
	gridspot1 = gridboard.spot[1, 1]
	graphpawn = graphboard.pawn[2]
	gridpawn = gridboard.pawn[2]
	idle_until(
		lambda: almost(graphpawn.x, locspot0.right),
		100,
		f"Never positioned pawn to 0's right (it's at {graphpawn.x}"
		f", not {locspot0.right})",
	)
	idle_until(
		lambda: almost(graphpawn.y, locspot0.top),
		100,
		"Never positioned pawn to 0's top",
	)
	idle_until(
		lambda: almost(gridpawn.pos, gridspot0.pos),
		100,
		"Never positioned pawn to grid 0, 0",
	)
	app.mainscreen.next_turn()
	idle_until(lambda: not app.edit_locked, 100, "Never unlocked")

	loc = app.engine.character["physical"].thing[2]["location"]

	def relocated_to(dest):
		nonlocal loc
		loc = app.engine.character["physical"].thing[2]["location"]
		return loc == dest

	idle_until(
		partial(relocated_to, (1, 1)),
		1000,
		f"Thing 2 didn't go to location (1, 1); instead, it's at {loc}",
	)
	idle_until(
		lambda: almost(graphpawn.x, locspot1.right),
		100,
		"Never positioned pawn to 1's right "
		f"(pawn is at {graphpawn.x} not {locspot1.right})",
	)
	idle_until(
		lambda: almost(graphpawn.y, locspot1.top),
		100,
		"Never positioned pawn to 1's top "
		f"(it's at {graphpawn.y}, not {locspot1.top})",
	)
	idle_until(
		lambda: almost(gridpawn.pos, gridspot1.pos),
		100,
		"Never positioned pawn to grid 1, 1",
	)
	locspot9 = graphboard.spot[9]
	app.mainscreen.next_turn()
	idle_until(lambda: not app.edit_locked, 100, "Never unlocked")
	loc = app.engine.character["physical"].thing[2]["location"]
	idle_until(
		partial(relocated_to, 9),
		1000,
		f"Thing 2 didn't relocate to 9; it's at {loc}",
	)
	idle_until(
		lambda: 2 not in gridboard.pawn,
		100,
		"pawn never removed from grid",
	)
	idle_until(
		lambda: almost(graphpawn.x, locspot9.right)
		and almost(graphpawn.y, locspot9.top),
		100,
		f"Never positioned pawn to 9's top-right, "
		f"it's at {graphpawn.pos} not {locspot9.right, locspot9.top}",
	)
	app.mainscreen.next_turn()
	idle_until(lambda: not app.edit_locked, 100, "Never unlocked")
	loc = app.engine.character["physical"].thing[2]["location"]
	idle_until(
		partial(relocated_to, (0, 0)),
		1000,
		f"Thing 2 didn't relocate to (0, 0); it's at {loc}",
	)
	idle_until(lambda: 2 in gridboard.pawn, 100, "pawn never returned to grid")
	idle_until(
		lambda: almost(graphpawn.x, locspot0.right)
		and almost(graphpawn.y, locspot0.top),
		100,
		f"Never returned to 0's top-right "
		f"(stuck at {graphpawn.pos}, should be "
		f"{locspot0.right, locspot0.top})",
	)
	idle_until(
		lambda: almost(gridpawn.pos, gridspot0.pos),
		100,
		"Never returned to grid 0, 0",
	)
