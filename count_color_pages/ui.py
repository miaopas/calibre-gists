#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai


__license__   = 'GPL v3'
__copyright__ = '2011, Kovid Goyal <kovid@kovidgoyal.net>'
__docformat__ = 'restructuredtext en'
from qt.core import QDialog, QVBoxLayout, QPushButton, QMessageBox, QLabel
from calibre.gui2 import error_dialog, question_dialog
from calibre.utils.logging import Log
from calibre.libunzip import extract as zipextract
from calibre.ptempfile import TemporaryDirectory
from calibre import CurrentDir, guess_type
from calibre.ebooks.oeb.polish.container import get_container
from pathlib import Path
from datetime import datetime
from calibre.utils.iso8601 import utc_tz, local_tz
import xml.etree.ElementTree as ET

from calibre_plugins.count_color_pages.dialogs import QueueProgressDialogCountColorPages
try:
    from PyQt5.Qt import QToolButton, QMenu
except ImportError:
    from PyQt4.Qt import QToolButton, QMenu

if False:
    # This is here to keep my python error checker from complaining about
    # the builtin functions that will be defined by the plugin loading system
    # You do not need this code in your plugins
    get_icons = get_resources = None

# The class that all interface action plugins must inherit from
from calibre.gui2.actions import InterfaceAction


class InterfacePlugin(InterfaceAction):

    name = '彩页数量'

    # Declare the main action associated with this plugin
    # The keyboard shortcut can be None if you dont want to use a keyboard
    # shortcut. Remember that currently calibre has no central management for
    # keyboard shortcuts, so try to use an unusual/unused shortcut.
    action_spec = ('彩页数量', None,
            '彩页数量', None)

    def genesis(self):
        
        icon = get_icons('images/icon.png')
        self.qaction.setIcon(icon)
        self.qaction.triggered.connect(self.action_count_color_pages)

    def get_book_ids(self):
        rows = self.gui.library_view.selectionModel().selectedRows()
        if not rows or len(rows) == 0:
            return 
        return self.gui.library_view.get_selected_ids()


    def action_count_color_pages(self):
        if question_dialog(self.gui,'彩页数量','计算彩页数量？'):
            book_ids = self.get_book_ids()
            if book_ids:
                self.count_color_pages(book_ids)

    def count_color_pages(self, book_ids):
        
        db = self.gui.current_db.new_api
        d = QueueProgressDialogCountColorPages(self.gui, book_ids, db)
        d.show()

        self.gui.library_view.model().refresh_ids(
            list(book_ids))


