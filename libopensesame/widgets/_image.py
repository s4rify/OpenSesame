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
from libopensesame import misc
from libopensesame.widgets._widget import widget
try: # Try both import statements
	from PIL import Image
except:
	import Image
from libopensesame.exceptions import osexception
import os

class image(widget):

	"""
	desc: |
		The image widget is used to display a non-interactive image.

		__Example (OpenSesame script):__

		~~~
		widget 0 0 1 1 image path='5.png'
		~~~

		__Example (Python):__

		~~~ {.python}
		from libopensesame import widgets
		form = widgets.form(exp)
		# The full path to the image needs to be provided.
		# self.experiment.pool can be used to retrieve the full path
		# to an image in the file pool.
		image = widgets.image(form, path=pool['5.png'])
		form.set_widget(image, (0,0))
		form._exec()
		~~~

		__Function list:__

		%--
		toc:
			mindepth: 2
			maxdepth: 2
		--%
	"""

	def __init__(self, form, path=None, adjust=True, frame=False):

		"""
		desc:
			Constructor.

		arguments:
			form:
				desc:	The parent form.
				type:	form

		keywords:
			path:
				desc:	The full path to the image. To show an image from the
						file pool, you need to first use `experiment.get_file`
						to determine the full path to the image.
				type:	[str, unicode, NoneType]
			adjust:
				desc:	Indicates whether the image should be scaled according
						to the size of the widget.
				type:	bool
			frame:
				desc:	Indicates whether a frame should be drawn around the
						widget.
				type:	bool
		"""

		if type(adjust) != bool:
			adjust = adjust == u'yes'
		if type(frame) != bool:
			frame = frame == u'yes'

		widget.__init__(self, form)
		self.adjust = adjust
		self.frame = frame
		self.path = path
		self.type = u'image'

	def render(self):

		"""
		desc:
			Draws the widget.
		"""

		_path = safe_str(self.path, enc=misc.filesystem_encoding())
		if not os.path.exists(_path):
			raise osexception(
				u'No valid path has been specified in image widget')
		x, y, w, h = self.rect
		x += w/2
		y += h/2
		self.form.canvas.image(_path, x=x, y=y, scale=self.scale,
			center=True)
		if self.frame:
			self.draw_frame(self.rect)

	def set_rect(self, rect):

		"""
		desc:
			Sets the widget geometry.

		arguments:
			rect:
				desc:	A (left, top, width, height) tuple.
				type:	tuple
		"""

		self.rect = rect
		_path = safe_str(self.path, enc=misc.filesystem_encoding())
		if not os.path.isfile(_path):
			raise osexception(u'"%s" does not exist' % _path)
		if self.adjust:
			x, y, w, h = self.rect
			try:
				img = Image.open(_path)
				img_w, img_h = img.size
			except:
				try:
					import pygame
					img = pygame.image.load(_path)
				except:
					raise osexception(
						u'Failed to open image "%s". Perhaps the file is not an image, or the image format is not supported.' \
						% self.path)
				img_w, img_h = img.get_size()
			scale_x = 1.*w/img_w
			scale_y = 1.*h/img_h
			self.scale = min(scale_x, scale_y)
		else:
			self.scale = 1
