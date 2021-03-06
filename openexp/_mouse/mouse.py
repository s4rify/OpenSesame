#-*- coding:utf-8 -*-

"""
This file is part of OpenSesame.

OpenSesame is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

OpenSesame is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with OpenSesame.  If not, see <http://www.gnu.org/licenses/>.
"""

from libopensesame.py3compat import *
from openexp.backend import backend, configurable
from libopensesame.exceptions import osexception
import warnings

class mouse(backend):

	"""
	desc: |
		The `mouse` class is used to collect mouse input.

		__Example:__

		~~~ .python
		# Draw a 'fixation-dot mouse cursor' until a button is clicked
		my_mouse = mouse()
		my_canvas = canvas()
		while True:
			button, position, timestamp = my_mouse.get_click(timeout=20)
			if button is not None:
				break
			(x,y), time = my_mouse.get_pos()
			my_canvas.clear()
			my_canvas.fixdot(x, y)
			my_canvas.show()
		~~~

		__Overview:__

		%--
		toc:
			mindepth: 2
			maxdepth: 3
		--%

		## Things to know

		### Coordinates

		- When *Uniform coordinates* is set to 'yes', coordinates are
		  relative to the center of the display. That is, (0,0) is the center.
		  This is the default as of OpenSesame 3.0.0.
		- When *Uniform coordinates* is set to 'no', coordinates are relative to
		  the top-left of the display. That is, (0,0) is the top-left. This was
		  the default in OpenSesame 2.9.X and earlier.

		### Button numbers

		Mouse buttons are numbered as follows:

		1. Left button
		2. Middle button
		3. Right button
		4. Scroll up
		5. Scroll down

		### Touch screens

		When working with a touch screen, a touch is registered as button 1
		(left button).

		### Response keywords

		Functions that accept `**resp_args` take the following keyword
		arguments:

		- `timeout` specifies a timeout value in milliseconds, or is set to
		  `None` to disable the timeout.
		- `buttonlist` specifies a list of buttons that are accepted, or is set
		  to `None` accept all keys.
		- `visible` indicates whether the mouse cursor becomes visible when a
		  click is collected (`True` or `False`). To immediately change cursor
		  visibility, use [mouse.show_cursor].

		~~~ .python
		# Get a left or right button press with a timeout of 3000 ms
		my_mouse = mouse()
		button, time = my_mouse.get_key(buttonlist=[1,3], timeout=3000)
		~~~

		Response keywords only affect the current operation (except when passed
		to [mouse.\_\_init\_\_][__init__]). To change the behavior for all
		subsequent operations, set the response properties directly:

		~~~ .python
		# Get two key left or right presses with a 5000 ms timeout
		my_mouse = mouse()
		my_mouse.keylist = [1,3]
		my_mouse.timeout = 5000
		button1, time1 = my_mouse.get_button()
		button2, time2 = my_mouse.get_button()
		~~~

		Or pass the response keywords to [mouse.\_\_init\_\_][__init__]:

		~~~ .python
		# Get two key left or right presses with a 5000 ms timeout
		my_mouse = mouse(keylist=[1,3], timeout=5000)
		button1, time1 = my_mouse.get_button()
		button2, time2 = my_mouse.get_button()
		~~~
	"""

	def __init__(self, experiment, **resp_args):

		"""
		desc: |
			Constructor to create a new `mouse` object. You do not generally
			call this constructor directly, but use the `mouse()` function,
			which is described here: [/python/common/]().

		arguments:
			experiment:
				desc:		The experiment object.
				type:		experiment

		keyword-dict:
			resp_args:
				Optional [response keywords] that will be used as the default
				for this `mouse` object.

		example: |
			my_mouse = mouse(buttonlist=[1, 2], timeout=2000)
		"""

		self.experiment = experiment
		self._cursor_shown = False
		backend.__init__(self, configurables={
			u'timeout' : self.assert_numeric_or_None,
			u'buttonlist' : self.assert_list_or_None,
			u'visible' : self.assert_bool,
			}, **resp_args)

	def set_config(self, **cfg):

		# Add synonyms to keylist
		if u'buttonlist' in cfg and isinstance(cfg[u'buttonlist'], list):
			try:
				cfg[u'buttonlist'] = \
					[int(button) for button in cfg[u'buttonlist']]
			except:
				raise osexception(
					u"buttonlist must be a list of numeric values, or None")
		backend.set_config(self, **cfg)

	def default_config(self):

		return {
			u'timeout' 			: None,
			u'buttonlist'		: None,
			u'visible'			: False
			}

	def show_cursor(self, show=True):

		"""
		desc: |
			Immediately changes the visibility of the mouse cursor.

			__Note:__ In most cases, you will want to use the `visible`
			[keyword][Response keywords], which changes the visibility during
			response collection, that is, while `mouse.get_click()` is called.

		keywords:
			show:
				desc: 	Indicates whether the cursor is shown (True) or hidden
						(False).
				type:	bool
		"""

		self._cursor_shown = show

	def set_pos(self, pos=(0,0)):

		"""
		desc: |
			Sets the position of the mouse cursor.

			__Warning:__ `set_pos()` is unreliable and will silently fail on
			some systems.

		keywords:
			pos:
				desc:	An (x,y) tuple for the new mouse coordinates.
				type:	tuple

		example: |
			my_mouse = mouse()
			my_mouse.set_pos(pos=(0,0))
		"""

		pass

	@configurable
	def get_click(self, **resp_args):

		"""
		desc:
			Collects a mouse click.

		keyword-dict:
			resp_args:
				Optional [response keywords] that will be used for this call to
				[mouse.get_click]. This does not affect subsequent operations.

		returns:
			desc:			A (button, position, timestamp) tuple. The button
							and position are `None` if a timeout occurs.
							Position is an (x, y) tuple in screen coordinates.
			type:			tuple

		example: |
			my_mouse = mouse()
			button, (x, y), timestamp = my_mouse.get_click(timeout=5000)
			if button is None:
				print('A timeout occurred!')
		"""

		raise NotImplementedError()

	def get_pos(self):

		"""
		desc:
			Returns the current position of the cursor.

		returns:
			desc:	A (position, timestamp) tuple.
			type:	tuple

		example: |
			my_mouse = mouse()
			(x, y), timestamp = my_mouse.get_pos()
			print('The cursor was at (%d, %d)' % (x, y))
		"""

		raise NotImplementedError()

	def get_pressed(self):

		"""
		desc:
			Returns the current state of the mouse buttons. A True value means
			the button is currently being pressed.

		returns:
			desc:	A (button1, button2, button3) tuple of boolean values.
			type:	tuple.

		example: |
			my_mouse = mouse()
			buttons = my_mouse.get_pressed()
			b1, b2, b3 = buttons
			print('Currently pressed mouse buttons: (%d,%d,%d)' % (b1,b2,b3))
		"""

		raise NotImplementedError()

	def flush(self):

		"""
		desc:
			Clears all pending input, not limited to the mouse.

		returns:
			desc:	True if a button had been clicked (i.e., if there was
					something to flush) and False otherwise.
			type:	bool

		example: |
			my_mouse = mouse()
			my_mouse.flush()
			button, position, timestamp = my_mouse.get_click()
		"""

		raise NotImplementedError()

	def synonyms(self, button):

		"""
		visible: False

		desc:
			Gives a list of synonyms for a mouse button. For example, 1 and
			'left_button' are synonyms.

		arguments:
			button:
				desc:	A button value.
				type:	[int, str, unicode]

		returns:
			desc:	A list of synonyms.
			type:	list
		"""

		button_map = [
			(1, u"left_button"),
			(2, u"middle_button"),
			(3, u"right_button"),
			(4, u"scroll_up"),
			(5, u"scroll_down")
			]
		for bm in button_map:
			if button in bm:
				return bm
		return []

	# Deprecated functions

	def set_buttonlist(self, buttonlist=None):

		"""
		visible:	False
		desc:		deprecated
		"""

		warnings.warn(u'mouse.set_buttonlist() has been deprecated. '
			'Use mouse.buttonlist instead.', DeprecationWarning)
		self.buttonlist = buttonlist

	def set_timeout(self, timeout=None):

		"""
		visible:	False
		desc:		deprecated
		"""

		warnings.warn(u'mouse.set_timeout() has been deprecated. '
			'Use mouse.timeout instead.', DeprecationWarning)
		self.timeout = timeout

	def set_visible(self, visible=True):

		"""
		visible:	False
		desc:		deprecated
		"""

		warnings.warn(u'mouse.set_visible() has been deprecated. '
			'Use mouse.visible instead.', DeprecationWarning)
		self.visible = visible
