#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai


__license__   = 'GPL v3'
__copyright__ = '2011, Kovid Goyal <kovid@kovidgoyal.net>'
__docformat__ = 'restructuredtext en'
from qt.core import QDialog, QVBoxLayout, QPushButton, QMessageBox, QLabel
from calibre.gui2 import error_dialog
from calibre.utils.logging import Log
from calibre.libunzip import extract as zipextract
from calibre.ptempfile import TemporaryDirectory
from calibre import CurrentDir, guess_type
from calibre.ebooks.oeb.polish.container import get_container
from pathlib import Path
import xml.etree.ElementTree as ET
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

    name = '阅读列表'

    # Declare the main action associated with this plugin
    # The keyboard shortcut can be None if you dont want to use a keyboard
    # shortcut. Remember that currently calibre has no central management for
    # keyboard shortcuts, so try to use an unusual/unused shortcut.
    action_spec = ('阅读列表', None,
            '阅读列表', None)

    def genesis(self):
        
        icon = get_icons('images/icon.png')
        self.qaction.setIcon(icon)
        self.qaction.triggered.connect(self.action_update_turn_direction_column)

    def get_book_ids(self):
        rows = self.gui.library_view.selectionModel().selectedRows()
        if not rows or len(rows) == 0:
            return error_dialog(self.gui, _('Cannot modify ePub'),
                _('You must select one or more books to perform this action.'), show=True)
        return set(self.gui.library_view.get_selected_ids())


    def action_update_turn_direction_column(self):
        book_ids = self.get_book_ids()
        print(book_ids)
        
        self.update_turn_direction_column(book_ids)

    def update_turn_direction_column(self, book_ids):
        
        db = self.gui.current_db.new_api
        for book_id in book_ids:
            
            # mi = db.get_metadata(book_id)
            # read_mi = mi.metadata_for_field('#read')
            # reading_mi = mi.metadata_for_field('#reading')
            readlist = db.field_for('#readlist', book_id)
            
            # not read -> reading -> finished
            
            if readlist is None:
                read_mi = True
            elif readlist is True:
                read_mi = None
             
            
    
            db.set_field('#readlist', {book_id:read_mi})

            print("finished writing to columns")
            print()
            # self.gui.library_view.selectionModel().clearSelection()
        # cr = self.gui.library_view.currentIndex().row()
        self.gui.library_view.model().refresh_ids(
            list(book_ids))
                
    def apply_settings(self):
        from calibre_plugins.reading_status.config import prefs
        # In an actual non trivial plugin, you would probably need to
        # do something based on the settings in prefs
        prefs

