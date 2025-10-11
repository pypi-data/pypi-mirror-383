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
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import (
	DictProperty,
	NumericProperty,
	ObjectProperty,
	StringProperty,
)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput

from .statlist import BaseStatListView
from .util import devour, load_kv, logwrap


class FloatInput(TextInput):
	@logwrap(section="FloatInput")
	def insert_text(self, s, from_undo=False):
		return super().insert_text(
			"".join(c for c in s if c in "0123456789."), from_undo
		)


class ControlTypePicker(Button):
	app = ObjectProperty()
	key = ObjectProperty()
	mainbutton = ObjectProperty()
	dropdown = ObjectProperty()
	set_control = ObjectProperty()

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.build()

	@logwrap(section="ControlTypePicker")
	def set_value(self, k, v):
		if v is None:
			del self.app.selected_proxy[k]
		else:
			self.app.selected_proxy[k] = v

	@logwrap(section="ControlTypePicker")
	def build(self, *_):
		app = App.get_running_app()
		if None in (self.key, self.set_control, app):
			Clock.schedule_once(self.build, 0)
			return
		binds = app._bindings
		self.mainbutton = None
		self.dropdown = None
		self.dropdown = DropDown()
		self.dropdown.bind(
			on_select=lambda instance, x: self.set_control(self.key, x)
		)
		readoutbut = Button(
			text="readout",
			size_hint_y=None,
			height=self.height,
			background_color=(0.7, 0.7, 0.7, 1),
		)
		while binds["ControlTypePicker", "readout", "on_release"]:
			readoutbut.unbind_uid(
				"on_release",
				binds["ControlTypePicker", "readout", "on_release"].pop(),
			)
		binds["ControlTypePicker", "readout", "on_release"].add(
			readoutbut.fbind(
				"on_release", lambda _: self.dropdown.select("readout")
			)
		)
		self.dropdown.add_widget(readoutbut)
		textinbut = Button(
			text="textinput",
			size_hint_y=None,
			height=self.height,
			background_color=(0.7, 0.7, 0.7, 1),
		)
		while binds["ControlTypePicker", "textinput", "on_release"]:
			textinbut.unbind_uid(
				"on_release",
				binds["ControlTypePicker", "textinput", "on_release"].pop(),
			)
		binds["ControlTypePicker", "textinput", "on_release"].add(
			textinbut.fbind(
				"on_release", lambda _: self.dropdown.select("textinput")
			)
		)
		self.dropdown.add_widget(textinbut)
		togbut = Button(
			text="togglebutton",
			size_hint_y=None,
			height=self.height,
			background_color=(0.7, 0.7, 0.7, 1),
		)
		while binds["ControlTypePicker", "togglebutton", "on_release"]:
			togbut.unbind_uid(
				"on_release",
				binds["ControlTypePicker", "togglebutton", "on_release"].pop(),
			)
		binds["ControlTypePicker", "togglebutton", "on_release"].add(
			togbut.fbind(
				"on_release", lambda _: self.dropdown.select("togglebutton")
			)
		)
		self.dropdown.add_widget(togbut)
		sliderbut = Button(
			text="slider",
			size_hint_y=None,
			height=self.height,
			background_color=(0.7, 0.7, 0.7, 1),
		)
		while binds["ControlTypePicker", "slider", "on_release"]:
			sliderbut.unbind_uid(
				"on_release",
				binds["ControlTypePicker", "slider", "on_release"].pop(),
			)
		binds["ControlTypePicker", "slider", "on_release"].add(
			sliderbut.fbind(
				"on_release", lambda _: self.dropdown.select("slider")
			)
		)
		self.dropdown.add_widget(sliderbut)
		while binds["ControlTypePicker", "on_release"]:
			self.unbind_uid(
				"on_release", binds["ControlTypePicker", "on_release"].pop()
			)
		binds["ControlTypePicker", "on_release"].add(
			self.fbind("on_release", self.dropdown.open)
		)
		app._unbinders.append(self.unbind_all)

	def unbind_all(self):
		binds = App.get_running_app()._bindings
		for uid in devour(binds["ControlTypePicker", "on_release"]):
			self.unbind_uid("on_release", uid)
		for button in self.dropdown.children[0].children:
			if not hasattr(button, "text"):
				continue
			for uid in devour(
				binds["ControlTypePicker", button.text, "on_release"]
			):
				button.unbind_uid("on_release", uid)


class ConfigListItemToggleButton(BoxLayout):
	true_text = StringProperty("0")
	false_text = StringProperty("1")

	@logwrap(section="ConfigListItemToggleButton")
	def set_true_text(self, *_):
		self.parent.set_config(
			self.parent.key, "true_text", self.ids.truetext.text
		)
		self.true_text = self.ids.truetext.text

	@logwrap(section="ConfigListItemToggleButton")
	def set_false_text(self, *_):
		self.parent.set_config(
			self.parent.key, "false_text", self.ids.falsetext.text
		)


class ConfigListItemSlider(BoxLayout):
	min = NumericProperty(0.0)
	max = NumericProperty(1.0)

	@logwrap(section="ConfigListItemSlider")
	def set_min(self, *_):
		minn = float(self.ids.minimum.text)
		try:
			self.parent.set_config(self.parent.key, "min", minn)
			self.min = minn
		except ValueError:
			self.ids.minimum.text = ""

	@logwrap(section="ConfigListItemSlider")
	def set_max(self, *_):
		maxx = float(self.ids.maximum.text)
		try:
			self.parent.set_config(self.parent.key, "max", maxx)
			self.max = maxx
			self.ids.maximum.hint_text = str(maxx)
		except ValueError:
			self.ids.maximum.text = ""


class ConfigListItemCustomizer(BoxLayout):
	key = ObjectProperty()
	control = StringProperty()
	config = DictProperty()
	set_config = ObjectProperty()

	@logwrap(section="ConfigListItemCustomizer")
	def on_control(self, *_):
		self.clear_widgets()
		if self.control == "togglebutton":
			if (
				"true_text" not in self.config
				or "false_text" not in self.config
			):
				Clock.schedule_once(self.on_control, 0)
				return
			wid = self._toggle = ConfigListItemToggleButton(
				true_text=self.config["true_text"],
				false_text=self.config["false_text"],
			)
			self.add_widget(wid)
		elif self.control == "slider":
			if "min" not in self.config or "max" not in self.config:
				Clock.schedule_once(self.on_control, 0)
				return
			wid = self._slider = ConfigListItemSlider(
				min=self.config["min"], max=self.config["max"]
			)
			self.add_widget(wid)

	@logwrap(section="ConfigListItemCustomizer")
	def on_config(self, *_):
		if hasattr(self, "_toggle"):
			if "true_text" in self.config:
				self._toggle.true_text = self.config["true_text"]
			if "false_text" in self.config:
				self._toggle.false_text = self.config["false_text"]
		if hasattr(self, "_slider"):
			if "min" in self.config:
				self._slider.min = self.config["min"]
			if "max" in self.config:
				self._slider.max = self.config["max"]


class ConfigListItem(BoxLayout):
	key = ObjectProperty()
	config = DictProperty()
	set_control = ObjectProperty()
	set_config = ObjectProperty()
	deleter = ObjectProperty()


class StatListViewConfigurator(BaseStatListView):
	statlist = ObjectProperty()
	_key_cfg_setters = DictProperty()
	_val_text_setters = DictProperty()
	_control_wids = DictProperty()

	@logwrap(section="ConfigListItemCustomizer")
	def set_control(self, key, value):
		config = self.proxy.get("_config", {})
		if value == "slider":
			if "min" not in config:
				self.set_config(key, "min", 0.0)
			if "max" not in config:
				self.set_config(key, "max", 1.0)
		elif value == "togglebutton":
			if "true_text" not in config:
				self.set_config(key, "true_text", "1")
			if "false_text" not in config:
				self.set_config(key, "false_text", "0")
		self.set_config(key, "control", value)

	@logwrap(section="ConfigListItemCustomizer")
	def munge(self, k, v):
		# makes ConfigListItem
		ret = super().munge(k, v)
		ret["deleter"] = self.del_key
		ret["set_control"] = self.set_control
		ret["set_config"] = self.set_config
		return ret


class StatScreen(Screen):
	statlist = ObjectProperty()
	statcfg = ObjectProperty()
	toggle = ObjectProperty()
	proxy = ObjectProperty()

	@property
	def engine(self):
		return App.get_running_app().engine

	@logwrap(section="ConfigListItemCustomizer")
	def new_stat(self):
		"""Look at the key and value that the user has entered into the stat
		configurator, and set them on the currently selected
		entity.

		"""
		key = self.ids.newstatkey.text
		value = self.ids.newstatval.text
		if not (key and value):
			# TODO implement some feedback to the effect that
			# you need to enter things
			return
		try:
			self.proxy[key] = self.engine.unpack(value)
		except (TypeError, ValueError):
			self.proxy[key] = value
		self.ids.newstatkey.text = ""
		self.ids.newstatval.text = ""

	def __init__(self, **kw):
		load_kv("statcfg.kv")
		super().__init__(**kw)
