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

    name = 'Add blank'

    # Declare the main action associated with this plugin
    # The keyboard shortcut can be None if you dont want to use a keyboard
    # shortcut. Remember that currently calibre has no central management for
    # keyboard shortcuts, so try to use an unusual/unused shortcut.
    action_spec = ('Add blank', None,
            'Add blank', None)

    def genesis(self):
        
        icon = get_icons('images/icon.png')
        self.qaction.setIcon(icon)
        self.qaction.triggered.connect(self.action_change_turn_direction)


        # self.create_menu_action(self.menu, "切换左右", "切换左右", icon=None,
        # description="切换书籍左右", triggered=self.action_change_turn_direction)
        # self.menu.aboutToShow.connect(self.about_to_show_menu)


    def get_book_ids(self):
        rows = self.gui.library_view.selectionModel().selectedRows()
        if not rows or len(rows) == 0:
            return error_dialog(self.gui, _('Cannot modify ePub'),
                _('You must select one or more books to perform this action.'), show=True)
        return set(self.gui.library_view.get_selected_ids())



    def action_change_turn_direction(self):
        book_ids = self.get_book_ids()
        
        db = self.gui.current_db.new_api
        id_pageturn = []
        for book_id in book_ids:
            mi = db.get_metadata(book_id)

            if db.has_format(book_id, 'EPUB'):
                fmt = 'EPUB'
            else:
                fmt = None

            if fmt:

                db.save_original_format(book_id, fmt)
                epub_path = db.format_abspath(book_id, fmt)
                # with TemporaryDirectory('_modify-epub') as tdir:
                #     with CurrentDir(tdir):
                container = get_container(epub_path, tweak_mode=True)
                data = """<?xml version='1.0' encoding='utf-8'?>
                            <html xmlns="http://www.w3.org/1999/xhtml">
                            <head>
                              
                            </head>

                            <body>
                                
                            </body>
                            </html>"""
                container.add_file('blank.html',data.encode('utf-8'),spine_index=1)


                # commit the changes
                container.commit()

                print("finished edit books")
        self.gui.library_view.model().refresh_ids(list(book_ids))
        self.gui.library_view.model().refresh_ids(list(book_ids),
                                      current_row=self.gui.library_view.currentIndex().row())



    def apply_settings(self):
        from calibre_plugins.add_blank.config import prefs
        # In an actual non trivial plugin, you would probably need to
        # do something based on the settings in prefs
        prefs

