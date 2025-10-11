# This file is part of Elide, frontend to Lisien, a framework for life simulation games.
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
from functools import partial

from kivy.clock import Clock
from kivy.properties import (
	BooleanProperty,
	BoundedNumericProperty,
	DictProperty,
	ListProperty,
	NumericProperty,
	ObjectProperty,
	OptionProperty,
	StringProperty,
)
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.slider import Slider
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget

from elide.util import logwrap

wraplog_CalendarWidget = partial(logwrap, section="CalendarWidget")


class CalendarWidget(Widget, RecycleDataViewBehavior):
	"""Base class for widgets within a Calendar

	Shows the value of its ``key`` at a particular ``turn``, and sets
	it at that turn if the value changes.

	"""

	turn = NumericProperty()
	"""What turn I'm displaying the stat's value for"""
	key = ObjectProperty()
	"""The key to set in the entity"""
	val = ObjectProperty(allownone=True)
	"""The value you want to set the key to"""

	@logwrap(section="CalendarWidget")
	def _update_disabledness(self, *_, **__):
		if not self.parent:
			return
		self.disabled = self.turn < self.parent.parent.entity.engine.turn

	@logwrap(section="CalendarWidget")
	def _trigger_update_disabledness(self, *_, **__):
		if hasattr(self, "_scheduled_update_disabledness"):
			Clock.unschedule(self._scheduled_update_disabledness)
		self._scheduled_update_disabledness = Clock.schedule_once(
			self._update_disabledness
		)

	@logwrap(section="CalendarWidget")
	def _set_value(self):
		entity = self.parent.parent.entity
		entity = getattr(entity, "stat", entity)
		entity[self.key] = self.val

	@logwrap(section="CalendarWidget")
	def on_val(self, *_):
		# do I want to do some validation at this point?
		# Maybe I should validate on the proxy objects and catch that in Calendar,
		# display an error message?
		if not self.parent:
			return
		calendar = self.parent.parent
		my_dict = calendar.idx[(self.turn, self.key)]
		entity = calendar.entity
		update_mode = calendar.update_mode
		if my_dict["val"] != self.val:
			my_dict["val"] = self.val
			if update_mode == "batch":
				calendar.changed = True
			elif update_mode == "present":
				if self.turn == entity.engine.turn:
					self._set_value()
				else:
					calendar.changed = True
			else:
				eng = entity.engine
				now = eng.turn
				if now == self.turn:
					self._set_value()
				else:
					eng.turn = self.turn
					self._set_value()
					eng.turn = now

	@logwrap(section="CalendarWidget")
	def on_parent(self, *_):
		if not self.parent:
			return
		self._trigger_update_disabledness()
		self.parent.parent.entity.engine.time.connect(
			self._trigger_update_disabledness
		)


class CalendarLabel(CalendarWidget, Label):
	def __init__(self, **kwargs):
		if "text" not in kwargs or not kwargs["text"]:
			kwargs["text"] = ""
		super().__init__(**kwargs)


class CalendarSlider(Slider, CalendarWidget):
	def on_val(self, *_):
		try:
			self.value = float(self.val)
		except ValueError:
			self.value = 0.0

	@partial(logwrap, section="CalendarSlider")
	def on_value(self, *_):
		self.val = self.value


class CalendarTextInput(CalendarWidget, TextInput):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self._trigger_parse_text = Clock.create_trigger(self._parse_text)

	@logwrap(section="CalendarTextInput")
	def _parse_text(self, *_):
		from ast import literal_eval

		try:
			v = literal_eval(self.text)
		except (TypeError, ValueError, SyntaxError):
			v = self.text
		self.val = v
		self.hint_text = repr(v)
		self.text = ""


wraplog_CalendarOptionButton = partial(logwrap, section="CalendarOptionButton")


class CalendarOptionButton(CalendarWidget, Button):
	options = ListProperty()
	modalview = ObjectProperty()
	cols = BoundedNumericProperty(1, min=1)

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self._make_modalview()
		self._update_modalview()
		binds = App.get_running_app()._bindings
		binds["CalendarOptionButton", id(self), "cols"].add(
			self.fbind("cols", self._make_modalview)
		)
		binds["CalendarOptionButton", id(self), "options"].add(
			self.fbind("options", self._update_modalview)
		)
		binds["CalendarOptionButton", id(self), "on_release"].add(
			self.fbind("on_release", self.modalview.open)
		)

	@logwrap(section="CalendarOptionButton")
	def _make_modalview(self, *_):
		if not self.modalview:
			self.modalview = ModalView()
		if self.modalview.children:
			container = self.modalview.children[0]
		else:
			container = GridLayout(cols=self.cols)
			self.modalview.add_widget(container)
		container.size = container.minimum_size
		self._update_modalview()

	@logwrap(section="CalendarOptionButton")
	def _update_modalview(self, *_):
		if not self.modalview:
			Clock.schedule_once(self.on_options, 0)
			return
		if not self.modalview.children:
			container = GridLayout(cols=self.cols)
			self.modalview.add_widget(container)
		else:
			container = self.modalview.children[0]
		for option in self.options:
			if type(option) is tuple:
				text, value = option
				container.add_widget(
					Button(
						size_hint_y=None,
						height=30,
						text=text,
						on_release=partial(self._set_value_and_close, value),
					)
				)
			else:
				container.add_widget(
					Button(
						text=str(option),
						on_release=partial(
							self._set_value_and_close, str(option)
						),
						size_hint_y=None,
						height=30,
					)
				)
		container.size = container.minimum_size

	@logwrap(section="CalendarOptionButton")
	def _set_value_and_close(self, val, *_):
		self.val = val
		self.modalview.dismiss()


class CalendarToggleButton(CalendarWidget, ToggleButton):
	index = None
	true_text = StringProperty("True")
	false_text = StringProperty("False")

	@logwrap(section="CalendarToggleButton")
	def on_state(self, *_):
		self.val = self.state == "down"
		self.text = self.true_text if self.val else self.false_text


class CalendarMenuLayout(LayoutSelectionBehavior, RecycleBoxLayout):
	pass


class CalendarBehavior:
	_control2wid = {
		"slider": "CalendarSlider",
		"togglebutton": "CalendarToggleButton",
		"textinput": "CalendarTextInput",
		"option": "CalendarOptionButton",
	}
	cols = NumericProperty(1)
	"""Number of columns to display, default 1"""
	entity = ObjectProperty()
	"""The lisien proxy object to display the stats of"""
	idx = DictProperty()
	"""Dictionary mapping ``key, turn`` pairs to their widgets"""
	changed = BooleanProperty(False)
	"""Whether there are changes yet to be committed to the lisien core"""
	update_mode = OptionProperty("batch", options=["batch", "present", "all"])
	"""How to go about submitting changes to the lisien core. Options:
	
	* ``'batch'`` (default): don't submit changes automatically. You have to call
	``get_track`` and apply the changes using the ``lisien.handle`` method
	``apply_choices``, eg.
		``engine_proxy.handle('apply_choices', choices=calendar.get_track())``
	* ``'present'``: immediately apply changes that affect the current turn,
	possibly wiping out anything in the future -- so you still have to use
	``get_track`` and ``apply_choices``. However, if you're using a calendar
	in the same interface as another control widget for the same stat,
	``'present'`` will ensure that the two widgets always display the same value.
	* ``'all'``: apply every change immediately to the lisien core. Should only be
	used when the lisien core is in planning mode.
	
	"""
	headers = BooleanProperty(True)
	"""Whether to display the name of the stat above its column, default ``True``"""
	turn_labels = BooleanProperty(True)
	"""Whether to display the turn of the value before its row, default ``True``"""
	turn_label_transformer = ObjectProperty(str)
	"""A function taking the turn number and returning a string to represent it
	
	Defaults to ``str``, but you might use this to display eg. the day of the
	week instead.
	
	"""
	data: ListProperty

	@logwrap(section="CalendarBehavior")
	def on_data(self, *_):
		idx = self.idx
		for item in self.data:
			if "key" in item and "turn" in item:
				idx[(item["turn"], item["key"])] = item

	@logwrap(section="CalendarBehavior")
	def get_track(self):
		"""Get a dictionary that can be used to submit my changes to ``lisien.Engine.apply_choices``

		If a data dictionary does not have the key 'turn', it will not be included in the track.
		You can use this to add labels and other non-input widgets to the calendar.

		"""
		changes = []
		track = {"entity": self.entity, "changes": changes}
		if not self.data:
			return track
		for datum in self.data:
			if "turn" in datum:
				break
		else:
			# I don't know *why* the calendar has no actionable data in it but here u go
			return track
		last = self.entity.engine.turn
		accumulator = []
		for datum in self.data:
			if "turn" not in datum:
				continue
			trn = datum["turn"]
			if trn < last:
				continue
			if trn > last:
				if trn > last + 1:
					changes.extend([[]] * (trn - last - 1))
				changes.append(accumulator)
				accumulator = []
				last = trn
			accumulator.append((datum["key"], datum["val"]))
		changes.append(accumulator)
		return track


class Agenda(RecycleView, CalendarBehavior):
	@logwrap(section="Agenda")
	def from_schedule(self, schedule, start_turn=None, key=str):
		# It should be convenient to style the calendar using data from the core;
		# not sure what the API should be like
		if not schedule:
			self.data = []
			return
		control2wid = self._control2wid
		if start_turn is None:
			start_turn = self.entity.engine.turn
		curturn = start_turn
		endturn = curturn + len(next(iter(schedule.values())))
		data = []
		stats = sorted(
			(
				stat
				for stat in schedule
				if not (isinstance(stat, str) and stat[0] == "_")
			),
			key=key,
		)
		headers = self.headers
		turn_labels = self.turn_labels
		if headers:
			if turn_labels:
				data.append({"widget": "Label", "text": ""})
			for stat in stats:
				if isinstance(stat, str) and stat[0] == "_":
					continue
				data.append(
					{"widget": "Label", "text": str(stat), "bold": True}
				)
		cols = len(data)
		iters = {stat: iter(values) for (stat, values) in schedule.items()}
		for turn in range(curturn, endturn):
			if turn_labels:
				data.append(
					{
						"widget": "Label",
						"text": self.turn_label_transformer(turn),
						"bold": True,
					}
				)
			if "_config" in iters:
				config = next(iters["_config"])
			else:
				config = None
			for stat in stats:
				datum = {"key": stat, "val": next(iters[stat]), "turn": turn}
				if config and stat in config and "control" in config[stat]:
					datum.update(config[stat])
					datum["widget"] = control2wid.get(
						datum.pop("control", None), "CalendarLabel"
					)
					if datum["widget"] == "CalendarToggleButton":
						if datum["val"]:
							datum["text"] = config[stat].get(
								"true_text", "True"
							)
							datum["state"] = "down"
						else:
							datum["text"] = config[stat].get(
								"false_text", "False"
							)
							datum["state"] = "normal"
					elif datum["widget"] == "CalendarTextInput":
						datum["hint_text"] = str(datum["val"])
				else:
					datum["widget"] = "CalendarLabel"
				data.append(datum)
		(self.cols, self.data, self.changed) = (cols, data, False)


wraplog_Calendar = partial(logwrap, section="Calendar")


class Calendar(RecycleView, CalendarBehavior):
	multicol = BooleanProperty(False)

	@logwrap(section="Calendar")
	def from_schedule(self, schedule, start_turn=None, key=str):
		if not schedule:
			self.data = []
			return
		control2wid = self._control2wid
		if start_turn is None:
			start_turn = self.entity.engine.turn
		curturn = start_turn
		endturn = curturn + len(next(iter(schedule.values())))
		data = []
		stats = sorted(
			(
				stat
				for stat in schedule
				if not (isinstance(stat, str) and stat[0] == "_")
			),
			key=key,
		)
		iters = {stat: iter(values) for (stat, values) in schedule.items()}
		headers = self.headers
		turn_labels = self.turn_labels
		for turn in range(curturn, endturn):
			if turn_labels:
				data.append(
					{
						"widget": "Label",
						"text": self.turn_label_transformer(turn),
						"bold": True,
					}
				)
			if "_config" in iters:
				config = next(iters["_config"])
			else:
				config = None
			for stat in stats:
				if headers:
					data.append(
						{"widget": "Label", "text": str(stat), "bold": True}
					)
				datum = {"key": stat, "val": next(iters[stat]), "turn": turn}
				if config and stat in config and "control" in config[stat]:
					datum.update(config[stat])
					datum["widget"] = control2wid.get(
						datum.pop("control", None), "CalendarLabel"
					)
					if datum["widget"] == "CalendarToggleButton":
						if datum["val"]:
							datum["text"] = config[stat].get(
								"true_text", "True"
							)
							datum["state"] = "down"
						else:
							datum["text"] = config[stat].get(
								"false_text", "False"
							)
							datum["state"] = "normal"
					elif datum["widget"] == "CalendarTextInput":
						datum["hint_text"] = str(datum["val"])
				else:
					datum["widget"] = "CalendarLabel"
				data.append(datum)
		if self.multicol:
			self.cols = endturn - curturn
		self.data = data


if __name__ == "__main__":
	from kivy.app import App

	class CalendarTestApp(App):
		def build(self):
			self.wid = Calendar()
			return self.wid

		def on_start(self):
			# it seems like the calendar blanks out its data sometime after initialization
			data = []
			for i in range(7):
				for j in range(3):
					data.append({"widget": "Button", "text": f"row{i} col{j}"})
			self.wid.data = data

	CalendarTestApp().run()
