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
from kivy.clock import Clock, triggered
from kivy.properties import ObjectProperty

from elide.kivygarden.texturestack import ImageStack

from .util import logwrap


def trigger(func):
	return triggered()(func)


class ImageStackProxy(ImageStack):
	proxy = ObjectProperty()
	name = ObjectProperty()

	@logwrap(section="ImageStackProxy")
	def finalize(self, initial=True):
		if getattr(self, "_finalized", False):
			return
		if self.proxy is None or not hasattr(self.proxy, "name"):
			Clock.schedule_once(self.finalize, 0)
			return
		binds = App.get_running_app()._bindings
		if initial:
			self.name = self.proxy.name
			if "_image_paths" in self.proxy:
				try:
					self.paths = self.proxy["_image_paths"]
				except Exception as ex:
					if not ex.args[0].startswith("Unable to load image type"):
						raise ex
					self.paths = self.default_image_paths
			else:
				self.paths = self.proxy.setdefault(
					"_image_paths", self.default_image_paths
				)
			self.finalize_children(initial)
		assert not binds["ImageStackProxy", self.name, "paths"]
		self._paths_binding = self.fbind(
			"paths", self._trigger_push_image_paths
		)
		binds["ImageStackProxy", self.name, "paths"].add(self._paths_binding)
		assert not binds["ImageStackProxy", self.name, "offxs"]
		self._offxs_binding = self.fbind("offxs", self._trigger_push_offxs)
		binds["ImageStackProxy", self.name, "offxs"].add(self._offxs_binding)
		assert not binds["ImageStackProxy", self.name, "offys"]
		self._offys_binding = self.fbind("offys", self._trigger_push_offys)
		binds["ImageStackProxy", self.name, "offys"].add(self._offys_binding)
		self._finalized = True

	@logwrap(section="ImageStackProxy")
	def finalize_children(self, initial=True, *_):
		for child in self.children:
			if not getattr(child, "_finalized", False):
				child.finalize(initial=initial)

	@logwrap(section="ImageStackProxy")
	def unfinalize(self):
		binds = App.get_running_app()._bindings
		binds["ImageStackProxy", self.name, "paths"].remove(
			self._paths_binding
		)
		self.unbind_uid("paths", self._paths_binding)
		binds["ImageStackProxy", self.name, "offxs"].remove(
			self._offxs_binding
		)
		self.unbind_uid("offxs", self._offxs_binding)
		binds["ImageStackProxy", self.name, "offys"].remove(
			self._offys_binding
		)
		self.unbind_uid("offys", self._offys_binding)
		self._finalized = False

	@logwrap(section="ImageStackProxy")
	def pull_from_proxy(self, *_):
		initial = not hasattr(self, "_finalized")
		self.unfinalize()
		for key, att in [
			("_image_paths", "paths"),
			("_offxs", "offxs"),
			("_offys", "offys"),
		]:
			if key in self.proxy and self.proxy[key] != getattr(self, att):
				setattr(self, att, self.proxy[key])
		self.finalize(initial)

	@logwrap(section="ImageStackProxy")
	def _trigger_pull_from_proxy(self, *args, **kwargs):
		if hasattr(self, "_scheduled_pull_from_proxy"):
			Clock.unschedule(self._scheduled_pull_from_proxy)
		self._scheduled_pull_from_proxy = Clock.schedule_once(
			self.pull_from_proxy, 0
		)

	@trigger
	@logwrap(section="ImageStackProxy")
	def _trigger_push_image_paths(self, *_):
		self.proxy["_image_paths"] = list(self.paths)

	@trigger
	@logwrap(section="ImageStackProxy")
	def _trigger_push_offxs(self, *_):
		self.proxy["_offxs"] = list(self.offxs)

	@trigger
	@logwrap(section="ImageStackProxy")
	def _trigger_push_offys(self, *_):
		self.proxy["_offys"] = list(self.offys)

	@trigger
	@logwrap(section="ImageStackProxy")
	def _trigger_push_stackhs(self, *_):
		self.proxy["_stackhs"] = list(self.stackhs)

	@trigger
	@logwrap(section="ImageStackProxy")
	def restack(self, *_):
		childs = sorted(
			list(self.children), key=lambda child: child.priority, reverse=True
		)
		self.clear_widgets()
		for child in childs:
			self.add_widget(child)
		self.do_layout()
