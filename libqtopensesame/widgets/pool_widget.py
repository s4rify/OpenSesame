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
from libopensesame import debug, misc
from libqtopensesame.misc import _
from libqtopensesame.misc.config import cfg
from libqtopensesame.widgets.base_widget import base_widget
from libqtopensesame._input.popup_menu import popup_menu
from libqtopensesame._input.confirmation import confirmation
from PyQt4 import QtCore, QtGui
import os
import os.path

class pool_widget(base_widget):

	"""
	desc:
		The file-pool widget.
	"""

	def __init__(self, main_window):

		"""
		desc:
			Constructor.

		arguments:
			main_window: The main-window object.
		"""

		self.max_len = 5
		super(pool_widget, self).__init__(main_window,
			ui=u'widgets.pool_widget')
		self.ui.button_pool_add.clicked.connect(self.select_and_add)
		self.ui.button_refresh.clicked.connect(self.refresh)
		self.ui.button_help_pool.clicked.connect(self.help)
		self.ui.button_browse_pool.clicked.connect(self.browse)
		self.ui.edit_pool_filter.textChanged.connect(self.refresh)
		self.ui.combobox_view.currentIndexChanged.connect(self.set_view)
		self.ui.list_pool.itemActivated.connect(self.activate_file)
		self.ui.list_pool.itemChanged.connect(self.rename_file)
		self.main_window.theme.apply_theme(self)
		self.ui.combobox_view.setItemIcon(0, self.main_window.theme.qicon(
			u"view-list-details"))
		self.ui.combobox_view.setItemIcon(1, self.main_window.theme.qicon(
			u"view-list-icons"))
		self.ui.label_size_warning.setVisible(False)

	def help(self):

		"""
		desc:
			Opens the help tab.
		"""

		self.main_window.ui.tabwidget.open_help(u"pool")

	def set_view(self):

		"""
		desc:
			Sets the viewmode (list/ icons) based on the gui control.
		"""

		if self.ui.combobox_view.currentIndex() == 0:
			self.ui.list_pool.setViewMode(QtGui.QListView.ListMode)
		else:
			self.ui.list_pool.setViewMode(QtGui.QListView.IconMode)

	def browse(self):

		"""
		desc:
			Opens the pool folder in the file manager in an OS specific way.
		"""

		misc.open_url(self.experiment.pool.folder())

	def add(self, files, rename=False):

		"""
		desc:
			Adds a list of files to the pool.

		arguments:
			files:
			 	desc:	A list of paths.
				type:	list
		"""

		if not files:
			return
		for path in files:
			basename = os.path.basename(path)
			if self.pool.in_folder(basename):
				if rename:
					while self.pool.in_folder(basename):
						basename = u'_' + basename
				else:
					c = confirmation(self.main_window,
						_(u"A file named '%s' already exists in the pool. Do you want to overwrite this file?") \
						% basename)
					if not c.show():
						continue
			try:
				self.pool.add(path, new_name=basename)
			except IOError as e:
				self.notify(_(u'Failed to copy %s to file pool') % path)
				self.console.write(safe_decode(e, errors=u'ignore'))
		self.refresh()
		self.select(basename)

	def select_and_add(self, dummy=None):

		"""
		desc:
			Adds one or more files to the pool.

		"""

		path_list = QtGui.QFileDialog.getOpenFileNames(
			self.main_window.ui.centralwidget, _(u"Add files to pool"),
			directory=cfg.default_pool_folder)
		if len(path_list) == 0:
			return
		cfg.default_pool_folder = os.path.dirname(str(path_list[0]))
		self.add(path_list)

	def select(self, fname):

		"""
		desc:
			Selects a specific file in the file pool.

		arguments:
			fname:
				desc:	The file to be selected.
				type:	[str, unicode]
		"""

		for i in range(self.ui.list_pool.count()):
			item = self.ui.list_pool.item(i)
			if item.text() == fname:
				self.ui.list_pool.setCurrentItem(item)

	def refresh(self):

		"""
		desc:
			Refreshes the contents of the pool widget.
		"""

		try:
			path_iterator = iter(self.pool)
		except Exception as e:
			self.notify(_(u'Failed to refresh file pool'))
			self.console.write(safe_decode(e, errors=u'ignore'))
			return
		filt = self.ui.edit_pool_filter.text().lower()
		self.ui.list_pool.clear()
		for path in path_iterator:
			debug.msg(path)
			fname = os.path.basename(path)
			if filt in fname.lower():
				icon = self.theme.qfileicon(self.pool[path])
				self.console.write(path)
				item = QtGui.QListWidgetItem(icon, fname)
				item.setFlags(item.flags()|QtCore.Qt.ItemIsEditable)
				item.icon = icon
				item.path = path
				item.setToolTip(path)
				self.ui.list_pool.addItem(item)
		try:
			size = self.pool.size()
		except:
			size = -1
		debug.msg(u'pool is %d bytes' % size)
		if size > cfg.file_pool_size_warning:
			self.ui.label_size_warning.setText(_('Your file pool is larger '
				'than usual (%d MB). This increases loading and saving time. '
				'Consider moving files from the file pool to the experiment '
				'folder.') % (size / 1048576))
			self.ui.label_size_warning.setVisible(True)
		else:
			self.ui.label_size_warning.setVisible(False)

	def open_file(self, path):

		"""
		desc:
			Opens a file in a platform specific way.

		arguments:
			path:
				desc:	The file to be opened.
				type:	[unicode, str]
		"""

		misc.open_url(self.pool[path])

	def activate_file(self, item):

		"""
		desc:
			Is called when a file is double-clicked or otherwise activated and
			opens the file.

		arguments:
			item:
				type:	QListWidgetItem
		"""

		self.open_file(item.path)

	def contextMenuEvent(self, event):

		"""
		desc:
			Presents a context menu.

		arguments:
			event:
			 	type:	QMouseClickEvent
		"""

		item = self.ui.list_pool.itemAt(self.ui.list_pool.mapFromGlobal(
			event.globalPos()))
		if item is None:
			return
		path = item.path
		pm = popup_menu(self, [
			(0, _(u'Open'), item.icon),
			(1, _(u'Remove from pool'), u'delete'),
			(2, _(u'Rename'), u'rename'),
			])
		action = pm.show()
		if action == 0:
			self.open_file(path)
		elif action == 1:
			self.delete_selected_files()
		elif action == 2:
			self.ui.list_pool.editItem(item)

	def delete_selected_files(self):

		"""
		desc:
			Deletes all selected files from the pool. Asks for confimation\
			first.
		"""

		# Prepare the confirmation dialog, which contains a limited nr of
		# filenames
		l = []
		suffix = u''
		for item in self.ui.list_pool.selectedItems()[:self.max_len]:
			l.append(str(item.text()))
		if len(self.ui.list_pool.selectedItems()) > self.max_len:
			suffix = _('And %d more file(s)') % \
				(len(self.ui.list_pool.selectedItems())-self.max_len)
		msg = _(u"<p>Are you sure you want to remove the following files from "
			u"the file pool? This operation will only affect the OpenSesame "
			u"file pool, not the original files on your disk.</p><p><b> - "
			u"%s</b></p><p>%s</p>") % (u"<br /> - ".join(l), suffix)
		c = confirmation(self.main_window, msg)
		if not c.show():
			return
		# Create a list of files to be removed
		dL = []
		for item in self.ui.list_pool.selectedItems():
			dL.append(item.path)
		# Remove the files
		try:
			for f in dL:
				del self.pool[f]
			debug.msg(u"removed '%s'" % f)
		except:
			debug.msg(u"failed to remove '%s'" % f)
		self.refresh()
		self.main_window.set_unsaved()

	def rename_file(self, item):

		"""
		desc:
			Starts a rename action for an item.

		arguments:
			item:
				type:	QListWidgetItem
		"""

		old_name = item.path
		new_name = item.text().strip()
		if new_name in self.pool:
			self.notify(
				_(u"There already is a file named '%s' in the file pool") \
				% new_name)
			new_name = old_name
		elif new_name in (old_name, u''):
			new_name = old_name
		else:
			try:
				self.pool.rename(old_name, new_name)
			except:
				self.notify(_(u'Failed to rename "%s" to "%s".') \
					% (old_name, new_name))
		self.refresh()
		self.select(new_name)

	def dragEnterEvent(self, event):

		"""
		desc:
			Accepts an incoming drag that precedes a drop.

		arguments:
			event:
			 	type:	QDragEnterEvent
		"""

		event.acceptProposedAction()

	def dropEvent(self, event):

		"""
		desc:
			Accepts an incoming drop.

		arguments:
			event:
			 	type:	QDropEnterEvent
		"""
		files = []
		for url in event.mimeData().urls():
			files.append(url.toLocalFile())
		self.add(files)
		event.acceptProposedAction()

	def focusInEvent(self, e):

		"""
		desc:
			Focus the filter edit when the widget receives focus.

		arguments:
			e:
				type:	QFocusEvent
		"""

		self.ui.edit_pool_filter.setFocus()

def select_from_pool(main_window, parent=None):

	"""
	desc:
		A static function that presents the select from pool dialog.

	arguments:
		main_window:	The GUI main window

	keywords:
		parent:		The parent QWidget or None to use main window's central
					widget.
	"""

	if parent is None:
		parent = main_window.ui.centralwidget
	d = QtGui.QDialog(parent)
	widget = pool_widget(main_window)
	widget.refresh()
	bbox = QtGui.QDialogButtonBox(d)
	bbox.addButton(_(u"Cancel"), QtGui.QDialogButtonBox.RejectRole)
	bbox.addButton(_(u"Select"), QtGui.QDialogButtonBox.AcceptRole)
	bbox.accepted.connect(d.accept)
	bbox.rejected.connect(d.reject)
	vbox = QtGui.QVBoxLayout()
	vbox.addWidget(widget)
	vbox.addWidget(bbox)
	d.setLayout(vbox)
	d.setWindowTitle(_(u"Select file from pool"))
	res = d.exec_()
	main_window.ui.pool_widget.refresh()
	if res == QtGui.QDialog.Rejected:
		return u""
	selected = widget.ui.list_pool.currentItem()
	if selected is None:
		return u""
	return selected.text()
