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
from functools import partial, wraps

from kivy.lang import Builder
from kivy.logger import Logger
from kivy.resources import resource_find
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview.layout import LayoutSelectionBehavior

from lisien.util import repr_call_sig


class SelectableRecycleBoxLayout(
	FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout
):
	pass


def load_kv(filename: str) -> None:
	"""Load a kv file unless it's already been loaded"""
	filename = resource_find(filename)
	if not filename:
		raise FileNotFoundError(filename)
	if filename in Builder.files:
		return
	Builder.load_file(filename)


def dummynum(character, name):
	"""Count how many nodes there already are in the character whose name
	starts the same.

	"""
	num = 0
	for nodename in character.node:
		nodename = str(nodename)
		if nodename[: len(name)] != name:
			continue
		try:
			nodenum = int(nodename.lstrip(name))
		except ValueError:
			continue
		num = max((nodenum, num))
	return num


def logwrap(func=None, *, section="ElideApp"):
	if func is None:
		return partial(logwrap, section=section)

	@wraps(func)
	def fn(*args, **kwargs):
		Logger.debug(section + ": " + repr_call_sig(func, *args, **kwargs))
		try:
			ret = func(*args, **kwargs)
		finally:
			for handler in Logger.handlers:
				# ensure any files get sync'd
				if hasattr(handler, "fd"):
					handler.fd.flush()
		return ret

	return fn


def devour(s):
	"""Iterate over items in s while removing them"""
	while s:
		yield s.pop()
