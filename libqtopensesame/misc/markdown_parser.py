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
from libqtopensesame.misc.base_subcomponent import base_subcomponent
import re
try:
	import markdown
except:
	markdown = None
try:
	from pygments import highlight
	if py3:
		from pygments.lexers import Python3TracebackLexer as TracebackLexer
		from pygments.lexers import Python3Lexer as PythonLexer
	else:
		from pygments.lexers import PythonTracebackLexer as TracebackLexer
		from pygments.lexers import PythonLexer as PythonLexer
	from pygments.formatters import HtmlFormatter
except:
	highlight = None

class markdown_parser(base_subcomponent):

	"""
	desc:
		A Markdown parser with syntax highlighting.
	"""

	def __init__(self, main_window):

		"""
		desc:
			Constructor.

		arguments:
			main_window:	The main-window object.
		"""

		self.setup(main_window)
		self.css = u'<style type="text/css">'
		with open(self.main_window.theme.resource(u'markdown.css')) as fd:
			self.css += fd.read()
		if highlight is not None:
			self.traceback_lexer = TracebackLexer()
			self.python_lexer = PythonLexer()
			self.html_formatter = HtmlFormatter()
			self.css += self.html_formatter.get_style_defs(u'.highlight')
			self.re_script = re.compile(
				r'^~~~\s*.(?P<syntax>\w+)(?P<script>.*?)^~~~', re.S | re.M)
		self.css += u'</style>'

	def highlight(self, md):

		"""
		desc:
			Replaces ~~~ blocks with syntax-highlighted HTML code.

		arguments:
			md:
				desc:	A Markdown  string.
				type:	str

		returns:
			desc:	A Markdown  string.
			type:	str
		"""

		if highlight is None:
			return md
		while True:
			m = re.search(self.re_script, md)
			if m is None:
				break
			orig = m.group()
			syntax = m.group(u'syntax')
			script = m.group(u'script')
			if syntax == u'traceback':
				lexer = self.traceback_lexer
			elif syntax == u'python':
				lexer = self.python_lexer
			else:
				md = md.replace(orig, u'<code>%s</code>\n' % script)
				continue
			new = highlight(script, lexer, self.html_formatter)
			md = md.replace(orig, new)
		return md

	def to_html(self, md):

		"""
		desc:
			Converts Markdown to HTML.

		arguments:
			md:
				desc:	A Markdown  string.
				type:	str

		returns:
			desc:	A Markdown  string.
			type:	str
		"""

		md = self.highlight(md)
		if markdown is None:
			return u'<pre>%s</pre>' % md
		return markdown.markdown(md, errors=u'ignore') + self.css
