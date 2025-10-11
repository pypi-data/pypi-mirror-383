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
"""Editors for textual data in the database.

The data is accessed via a "store" -- a mapping onto the table, used
like a dictionary. Each of the widgets defined here,
:class:`StringsEditor` and :class:`FuncsEditor`, displays a list of
buttons with which the user may select one of the keys in the store,
and edit its value in a text box.

"""

import re
import string
from ast import parse
from functools import partial
from textwrap import dedent, indent

from kivy.app import App
from kivy.clock import Clock, triggered
from kivy.logger import Logger
from kivy.properties import (
	AliasProperty,
	BooleanProperty,
	ListProperty,
	NumericProperty,
	ObjectProperty,
	StringProperty,
)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton

from .util import devour, load_kv, logwrap


def trigger(func):
	return triggered()(func)


class RecycleToggleButton(ToggleButton, RecycleDataViewBehavior):
	"""Toggle button at some index in a RecycleView"""

	index = NumericProperty()

	@logwrap(section="RecycleToggleButton")
	def on_touch_down(self, touch):
		if self.collide_point(*touch.pos):
			return self.parent.select_with_touch(self.index, touch)

	@logwrap(section="RecycleToggleButton")
	def apply_selection(self, rv, index, is_selected):
		if is_selected and index == self.index:
			self.state = "down"
		else:
			self.state = "normal"


class StoreButton(RecycleToggleButton):
	"""RecycleToggleButton to select something to edit in a Store"""

	store = ObjectProperty()
	"""Either a FunctionStore or a StringStore"""
	name = StringProperty()
	"""Name of this particular item"""
	source = StringProperty()
	"""Text of this item"""
	select = ObjectProperty()
	"""Function that gets called with my ``index`` when I'm selected"""

	@logwrap(section="RecycleToggleButton")
	def on_parent(self, *_):
		if self.name == "+":
			self.state = "down"
			self.select(self.index)

	@logwrap(section="RecycleToggleButton")
	def on_state(self, *_):
		if self.state == "down":
			self.select(self.index)


class StoreList(RecycleView):
	"""Holder for a :class:`kivy.uix.listview.ListView` that shows what's
	in a store, using one of the StoreAdapter classes.

	"""

	store = ObjectProperty()
	"""Either a FunctionStore or a StringStore"""
	selection_name = StringProperty()
	"""The ``name`` of the ``StoreButton`` currently selected"""
	boxl = ObjectProperty()
	"""Instance of ``SelectableRecycleBoxLayout``"""

	def __init__(self, **kwargs):
		self._i2name = {}
		self._name2i = {}
		super().__init__(**kwargs)
		App.get_running_app()._unbinders.append(self.unbind_all)

	def unbind_all(self):
		binds = App.get_running_app()._bindings
		for uid in devour(
			binds["StoreList", self.store._store, "boxl", "selected_nodes"]
		):
			self.boxl.unbind_uid("selected_nodes", uid)

	@logwrap(section="RecycleToggleButton")
	def on_store(self, *_):
		self.store.connect(self._trigger_redata)
		self.redata()

	@logwrap(section="RecycleToggleButton")
	def on_boxl(self, *_):
		if self.store is None:
			Clock.schedule_once(self.on_boxl, 0)
			return
		app = App.get_running_app()
		if not app:
			return
		binds = app._bindings[
			"StoreList", self.store._store, "boxl", "selected_nodes"
		]
		for uid in devour(binds):
			self.boxl.unbind_uid("selected_nodes", uid)
		binds.add(self.boxl.fbind("selected_nodes", self._pull_selection))

	@logwrap(section="RecycleToggleButton")
	def _pull_selection(self, *_):
		if not self.boxl.selected_nodes:
			return
		self.selection_name = self._i2name[self.boxl.selected_nodes[0]]

	@logwrap(section="RecycleToggleButton")
	def munge(self, datum):
		i, name = datum
		self._i2name[i] = name
		self._name2i[name] = i
		return {
			"store": self.store,
			"text": str(name),
			"name": name,
			"select": self.ids.boxl.select_node,
			"index": i,
		}

	@logwrap(section="RecycleToggleButton")
	def redata(self, *_, **kwargs):
		"""Update my ``data`` to match what's in my ``store``"""
		select_name = kwargs.get("select_name")
		if not self.store:
			Clock.schedule_once(self.redata)
			return
		self.data = list(
			map(self.munge, enumerate(sorted(self.store._cache.keys())))
		)
		if select_name:
			self._trigger_select_name(select_name)

	@logwrap(section="RecycleToggleButton")
	def _trigger_redata(self, *args, **kwargs):
		part = partial(self.redata, *args, **kwargs)
		if hasattr(self, "_scheduled_redata"):
			Clock.unschedule(self._scheduled_redata)
		self._scheduled_redata = Clock.schedule_once(part, 0)

	@logwrap(section="RecycleToggleButton")
	def select_name(self, name, *_):
		"""Select an item by its name, highlighting"""
		self.boxl.select_node(self._name2i[name])

	@logwrap(section="RecycleToggleButton")
	def _trigger_select_name(self, name):
		part = partial(self.select_name, name)
		if hasattr(self, "_scheduled_select_name"):
			Clock.unschedule(self._scheduled_select_name)
		self._scheduled_select_name = Clock.schedule_once(part, 0)


class LanguageInput(TextInput):
	"""Widget to enter the language you want to edit"""

	screen = ObjectProperty()
	"""The instance of ``StringsEdScreen`` that I'm in"""

	@logwrap(section="RecycleToggleButton")
	def on_focus(self, instance, value, *largs):
		if not value:
			if self.screen.language != self.text:
				self.screen.language = self.text
			self.text = ""


class StringsEdScreen(Screen):
	"""A screen in which to edit strings to be presented to humans

	Needs a ``toggle`` function to switch back to the main screen;
	a ``language`` identifier; and a ``language_setter`` function to be called
	with that ``language`` when changed.

	"""

	toggle = ObjectProperty()
	"""Function to switch back to the main screen"""
	language = StringProperty("eng")
	"""Code identifying the language we're editing"""
	edbox = ObjectProperty()
	"""Widget containing editors for the current string and its name"""

	def __init__(self, **kw):
		load_kv("stores.kv")
		super().__init__(**kw)

	@logwrap(section="RecycleToggleButton")
	def on_language(self, *_):
		if self.edbox is None:
			Clock.schedule_once(self.on_language, 0)
			return
		self.edbox.storelist.redata()
		if self.store.language != self.language:
			self.store.language = self.language

	@logwrap(section="RecycleToggleButton")
	def on_store(self, *_):
		self.language = self.store.language
		self.store.language.connect(self._pull_language)

	@logwrap(section="RecycleToggleButton")
	def _pull_language(self, *_, language):
		self.language = language

	@logwrap(section="RecycleToggleButton")
	def save(self, *_):
		if self.edbox is None:
			Clock.schedule_once(self.save, 0)
			return
		self.edbox.save()


class Editor(BoxLayout):
	"""Abstract widget for editing strings or functions"""

	name_wid = ObjectProperty()
	"""Text input widget holding the name of the string being edited"""
	store = ObjectProperty()
	"""Proxy to the ``FunctionStore`` or ``StringStore``"""
	disable_text_input = BooleanProperty(False)
	"""Whether to prevent text entry (not name entry)"""
	deletable = BooleanProperty(True)
	"""Whether to show a delete button"""
	# This next is the trigger on the EdBox, which may redata the StoreList
	_trigger_save = ObjectProperty()
	_trigger_delete = ObjectProperty()

	@logwrap(section="RecycleToggleButton")
	def save(self, *_):
		"""Put text in my store, return True if it changed"""
		if self.name_wid is None or self.store is None:
			Logger.debug(
				"{}: Not saving, missing name_wid or store".format(
					type(self).__name__
				)
			)
			return
		if not (self.name_wid.text or self.name_wid.hint_text):
			Logger.debug("{}: Not saving, no name".format(type(self).__name__))
			return
		if (
			self.name_wid.text
			and self.name_wid.text[0]
			in string.digits + string.whitespace + string.punctuation
		):
			# TODO alert the user to invalid name
			Logger.warning(
				"{}: Not saving, invalid name".format(type(self).__name__)
			)
			return
		if hasattr(self, "_do_parse"):
			try:
				parse(self.source)
			except SyntaxError:
				# TODO alert user to invalid source
				Logger.debug(
					"{}: Not saving, couldn't parse".format(
						type(self).__name__
					)
				)
				return
		do_redata = False
		if self.name_wid.text:
			if (
				self.name_wid.hint_text
				and self.name_wid.hint_text != self.name_wid.text
				and hasattr(self.store, self.name_wid.hint_text)
			):
				delattr(self.store, self.name_wid.hint_text)
				do_redata = True
			if (
				not hasattr(self.store, self.name_wid.text)
				or getattr(self.store, self.name_wid.text) != self.source
			):
				Logger.debug("{}: Saving!".format(type(self).__name__))
				setattr(self.store, self.name_wid.text, self.source)
				do_redata = True
		elif self.name_wid.hint_text:
			if (
				not hasattr(self.store, self.name_wid.hint_text)
				or getattr(self.store, self.name_wid.hint_text) != self.source
			):
				Logger.debug("{}: Saving!".format(type(self).__name__))
				setattr(self.store, self.name_wid.hint_text, self.source)
				do_redata = True
		return do_redata

	@logwrap(section="RecycleToggleButton")
	def delete(self, *_):
		"""Remove the currently selected item from my store"""
		key = self.name_wid.text or self.name_wid.hint_text
		if not hasattr(self.store, key):
			# TODO feedback about missing key
			return
		delattr(self.store, key)
		try:
			return min(kee for kee in dir(self.store) if kee > key)
		except ValueError:
			return "+"


class StringInput(Editor):
	"""Editor for human-readable strings"""

	validate_name_input = ObjectProperty()
	"""Boolean function for checking if a string name is acceptable"""

	def unbind_all(self):
		for uid in devour(
			App.get_running_app()._bindings["StringInput", "name_wid", "text"]
		):
			self.name_wid.unbind_uid("text", uid)

	@logwrap(section="StringInput")
	def on_name_wid(self, *_):
		if not self.validate_name_input:
			Clock.schedule_once(self.on_name_wid, 0)
			return
		app = App.get_running_app()
		binds = app._bindings
		binds["StringInput", "name_wid", "text"].add(
			self.name_wid.fbind("text", self.validate_name_input)
		)
		app._unbinders.append(self.unbind_all)

	@logwrap(section="StringInput")
	def _get_name(self):
		if self.name_wid:
			return self.name_wid.text

	@logwrap(section="StringInput")
	def _set_name(self, v, *_):
		if not self.name_wid:
			Clock.schedule_once(partial(self._set_name, v), 0)
			return
		self.name_wid.text = v

	name = AliasProperty(_get_name, _set_name)

	@logwrap(section="StringInput")
	def _get_source(self):
		if "string" not in self.ids:
			return ""
		return self.ids.string.text

	@logwrap(section="StringInput")
	def _set_source(self, v, *args):
		if "string" not in self.ids:
			Clock.schedule_once(partial(self._set_source, v), 0)
			return
		self.ids.string.text = v

	source = AliasProperty(_get_source, _set_source)


class EdBox(BoxLayout):
	"""Box containing most of an editor's screen

	Has a StoreList and an Editor, which in turn holds a name field and a big text entry box.

	"""

	storelist = ObjectProperty()
	"""An instance of ``StoreList``"""
	editor = ObjectProperty()
	"""An instance of a subclass of ``Editor``"""
	store = ObjectProperty()
	"""Proxy to the store I represent"""
	store_name = StringProperty()
	"""Name of my store, so I can get it from the engine"""
	data = ListProperty()
	"""Dictionaries describing widgets in my ``storelist``"""
	toggle = ObjectProperty()
	"""Function to show or hide my screen"""
	disable_text_input = BooleanProperty(False)
	"""Set to ``True`` to prevent entering text in the editor"""
	selection_name = StringProperty()

	@logwrap(section="EdBox")
	def on_store_name(self, *_):
		app = App.get_running_app()
		if not hasattr(app, "engine"):
			Clock.schedule_once(self.on_store_name, 0)
			return
		self.store = getattr(app.engine, self.store_name)
		app._unbinders.append(self.unbind_all)

	def unbind_all(self):
		binds = App.get_running_app()._bindings
		for uid in devour(
			binds["EdBox", self.store_name, "storelist", "selection_name"]
		):
			self.storelist.unbind_uid("selection_name", uid)

	@logwrap(section="EdBox")
	def on_storelist(self, *_):
		if not self.store_name:
			Clock.schedule_once(self.on_storelist, 0)
			return
		binds = App.get_running_app()._bindings[
			"EdBox", self.store_name, "storelist", "selection_name"
		]
		for uid in devour(binds):
			self.storelist.unbind_uid("selection_name", uid)
		binds.add(
			self.storelist.fbind(
				"selection_name", self.setter("selection_name")
			)
		)

	@trigger
	@logwrap(section="EdBox")
	def validate_name_input(self, *_):
		self.disable_text_input = not (
			self.valid_name(self.editor.name_wid.hint_text)
			or self.valid_name(self.editor.name_wid.text)
		)

	@logwrap(section="EdBox")
	def on_selection_name(self, _, selection_name):
		if selection_name == self.editor.name_wid.hint_text:
			return
		self.save()
		# The + button at the top is for adding an entry yet unnamed, so don't display hint text for it
		self.editor.name_wid.hint_text = selection_name.strip("+")
		self.editor.name_wid.text = ""
		try:
			self.editor.source = getattr(
				self.store, self.editor.name_wid.hint_text
			)
		except AttributeError:
			self.editor.source = self.get_default_text(
				self.editor.name_wid.hint_text
			)
		self.disable_text_input = not self.valid_name(
			self.editor.name_wid.hint_text
		)
		if hasattr(self, "_lock_save"):
			del self._lock_save

	@logwrap(section="EdBox")
	def dismiss(self, *_):
		self.save()
		self.toggle()

	@logwrap(section="EdBox")
	def save(self, *_, name=None):
		if not self.editor or not self.store:
			return
		if hasattr(self, "_lock_save"):
			return
		self._lock_save = True
		save_select = self.editor.save()
		if save_select:
			self.storelist.redata(select_name=name)
		else:
			del self._lock_save

	@logwrap(section="EdBox")
	def _trigger_save(self, name=None):
		part = partial(self.save, name=name)
		Clock.unschedule(part)
		Clock.schedule_once(part, 0)

	@logwrap(section="EdBox")
	def delete(self, *_):
		if not self.editor:
			return
		if hasattr(self, "_lock_save"):
			return
		self._lock_save = True
		del_select = self.editor.delete()
		if del_select:
			self.storelist.redata(del_select)
		else:
			del self._lock_save

	_trigger_delete = trigger(delete)

	def on_store(self, *_):
		pass


class StringNameInput(TextInput):
	"""Small text box for the names of strings"""

	_trigger_save = ObjectProperty()

	@logwrap(section="StringNameInput")
	def on_focus(self, inst, val, *largs):
		if self.text and not val:
			self._trigger_save(self.text)


class StringsEdBox(EdBox):
	"""Box containing most of the strings editing screen

	Contains the storelist and the editor, which in turn contains the string name input
	and a bigger input field for the string itself.

	"""

	language = StringProperty("eng")

	@staticmethod
	def get_default_text(newname):
		return ""

	@staticmethod
	def valid_name(name):
		return name and name[0] != "+"


sig_ex = re.compile(r"^ *def .+?\((.+)\):$")


class FunctionNameInput(TextInput):
	"""Input for the name of a function

	Filters out illegal characters.

	"""

	_trigger_save = ObjectProperty()

	@logwrap(section="FunctionNameInput")
	def insert_text(self, s, from_undo=False):
		if self.text == "":
			if s[0] not in (string.ascii_letters + "_"):
				return
		return super().insert_text(
			"".join(
				c
				for c in s
				if c in (string.ascii_letters + string.digits + "_")
			)
		)

	@logwrap(section="FunctionNameInput")
	def on_focus(self, inst, val, *_):
		if not val:
			self._trigger_save(self.text)


@logwrap(section="elide.stores")
def munge_source(v):
	"""Take Python source code, return a pair of its parameters and the rest of it dedented"""
	lines = v.split("\n")
	if not lines:
		return tuple(), ""
	firstline = lines[0].lstrip()
	while firstline == "" or firstline[0] == "@":
		del lines[0]
		firstline = lines[0].lstrip()
	if not lines:
		return tuple(), ""
	params = tuple(
		parm.strip() for parm in sig_ex.match(lines[0]).group(1).split(",")
	)
	del lines[0]
	if not lines:
		return params, ""
	# hack to allow 'empty' functions
	if lines and lines[-1].strip() == "pass":
		del lines[-1]
	return params, dedent("\n".join(lines))


class FuncEditor(Editor):
	"""The editor widget for working with any particular function.

	Contains a one-line field for the function's name and a multi-line
	field for its code.

	"""

	storelist = ObjectProperty()
	"""Instance of ``StoreList`` that shows all the functions you can edit"""
	codeinput = ObjectProperty()
	params = ListProperty(["obj"])
	params_disabled = BooleanProperty(True)
	params_text = StringProperty()
	name = StringProperty()
	_text = StringProperty()
	_do_parse = True

	def on_params_text(self, *_):
		if "params" not in self.ids:
			Clock.schedule_once(self.on_params_text, 0)
			return
		self.ids.params.text = self.params_text

	def _get_source(self):
		code = self.get_default_text(self.name or self.name_wid.text)
		if self._text:
			code += indent(self._text, " " * 4)
		else:
			code += " " * 4 + "pass"
		return code.rstrip(" \n\t")

	def unbind_all(self):
		for uid in devour(
			App.get_running_app()._bindings["FuncEditor", "codeinput", "text"]
		):
			self.codeinput.unbind_uid("text", uid)

	@logwrap(section="FuncEditor")
	def _set_source(self, v):
		if not self.codeinput:
			Clock.schedule_once(partial(self._set_source, v), 0)
			return
		binds = App.get_running_app()._bindings
		while binds["FuncEditor", "codeinput", "text"]:
			self.codeinput.unbind_uid(
				"text", binds["FuncEditor", "codeinput", "text"].pop()
			)
		self.params, self.codeinput.text = munge_source(str(v))
		binds["FuncEditor", "codeinput", "text"].add(
			self.codeinput.fbind("text", self.setter("_text"))
		)

	source = AliasProperty(_get_source, _set_source, bind=("_text", "params"))

	def get_default_text(self, name):
		if not name or name == "+":
			name = "a"
		return "def {}({}):\n".format(name, ", ".join(self.params))

	def on_codeinput(self, *args):
		app = App.get_running_app()
		app._unbinders.append(self.unbind_all)
		binds = app._bindings["FuncEditor", "codeinput", "text"]
		self._text = self.codeinput.text
		while binds:
			self.codeinput.unbind_uid("text", binds.pop())
		binds.add(self.codeinput.fbind("text", self.setter("_text")))


class MethodEditor(FuncEditor):
	def on_params_text(self, *_):
		params = self.params_text.split(", ")
		if self._validate_params(params):
			self.params = params

	@staticmethod
	def _validate_params(params: list[str]) -> bool:
		return params[0] == "self"


class FunctionEditor(MethodEditor):
	@staticmethod
	def _validate_params(params: list[str]) -> bool:
		return True


class FuncsEdBox(EdBox):
	"""Widget for editing the Python source of funcs to be used in lisien sims.

	Contains a list of functions in the store it's about, next to a
	FuncEditor showing the source of the selected one, and a close button.

	"""

	def get_default_text(self, newname):
		return self.editor.get_default_text(newname)

	@staticmethod
	def valid_name(name):
		return (
			name
			and name[0]
			not in string.digits + string.whitespace + string.punctuation
		)

	@logwrap(section="FuncsEdBox")
	def on_data(self, *_):
		app = App.get_running_app()
		if app is None:
			return
		app.rules.rulesview.set_functions(
			self.store_name, map(app.rules.rulesview.inspect_func, self.data)
		)


class FuncsEdScreen(Screen):
	"""Screen containing three FuncsEdBox

	Triggers, prereqs, and actions.

	"""

	toggle = ObjectProperty()

	def __init__(self, **kw):
		load_kv("stores.kv")
		super().__init__(**kw)

	@logwrap(section="FuncsEdScreen")
	def save(self, *args):
		self.ids.triggers.save()
		self.ids.prereqs.save()
		self.ids.actions.save()
