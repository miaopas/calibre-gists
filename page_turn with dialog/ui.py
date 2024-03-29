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
from calibre_plugins.page_turn.dialogs import QueueProgressDialogUpdateDirection,QueueProgressDialogChangeDirection
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

    name = '切换左右翻页'

    # Declare the main action associated with this plugin
    # The keyboard shortcut can be None if you dont want to use a keyboard
    # shortcut. Remember that currently calibre has no central management for
    # keyboard shortcuts, so try to use an unusual/unused shortcut.
    action_spec = ('切换左右翻页', None,
            '识别当前翻页方式', None)

    def genesis(self):
        self.menu = QMenu(self.gui)
        self.qaction.setMenu(self.menu)
        icon = get_icons('images/icon.png')
        self.qaction.setIcon(icon)
        self.qaction.triggered.connect(self.action_update_turn_direction_column)

        self.create_menu_action(self.menu, "切换左右", "切换左右", icon=None,
        description="切换书籍左右", triggered=self.action_change_turn_direction)
        # self.menu.aboutToShow.connect(self.about_to_show_menu)


    def get_book_ids(self):
        rows = self.gui.library_view.selectionModel().selectedRows()
        if not rows or len(rows) == 0:
            return error_dialog(self.gui, _('Cannot modify ePub'),
                _('You must select one or more books to perform this action.'), show=True)
        return list(self.gui.library_view.get_selected_ids())



    def action_change_turn_direction(self):
        book_ids = self.get_book_ids()
        
        db = self.gui.current_db.new_api
        d = QueueProgressDialogChangeDirection(self.gui, book_ids, db)
        d.show()

        if d.wasCanceled():
            return 

        self.update_turn_direction_column(book_ids)

    def action_update_turn_direction_column(self):
        book_ids = self.get_book_ids()
        print(book_ids)
        
        self.update_turn_direction_column(book_ids)

    def update_turn_direction_column(self, book_ids):
        
        db = self.gui.current_db.new_api

       
        d = QueueProgressDialogUpdateDirection(self.gui, book_ids, db)
        d.show()
        

        # self.gui.library_view.selectionModel().clearSelection()
        self.gui.library_view.model().refresh_ids(list(book_ids))
        self.gui.library_view.model().refresh_ids(list(book_ids),
                                      current_row=self.gui.library_view.currentIndex().row())
        
        
        # self.gui.library_view.selectionModel().reset()


    # def do_book(self, book_id):
    #     db = self.gui.current_db.new_api
    #     try:
    #         print(f'Current on {db.field_for("title", book_id)}')
    #         title = db.field_for("title", book_id)
    #         print(f'Current on {title}')
    #         if db.has_format(book_id, 'AZW3'):
    #             fmt = 'AZW3'
    #         elif db.has_format(book_id, 'EPUB'):
    #             fmt = 'EPUB'
    #         elif db.has_format(book_id, 'MOBI'):
    #             fmt = 'MOBI'
    #         else:
    #             fmt = None

    #         if fmt:
    #             epub_path = db.format_abspath(book_id, fmt)
    #             try:
    #                 container = get_container(epub_path, tweak_mode=True)
    #             except Exception as e:
    #                 raise Exception(str(e) + str(book_id))

    #             path = container.opf_dir + '/' + container.opf_name.split('/')[-1]
                

    #             print(f'container.opf_dir :  {container.opf_dir}')
    #             print(f'container.opf_name : {container.opf_name}')

    #             tree = ET.parse(path)
    #             root = tree.getroot()
    #             page_turn_mi = None
    #             for ele in root.getchildren():
    #                 if 'spine' in ele.tag:
    #                     if ele.attrib.get('page-progression-direction') is None or ele.attrib['page-progression-direction'] != 'rtl':
    #                         page_turn_mi =  'L to R'
    #                     elif ele.attrib['page-progression-direction'] == 'rtl':
    #                         page_turn_mi =  'R to L'
                
    #             db.set_field('#page_turn_direction', {book_id: page_turn_mi})

    #             print("finished writing to columns")
    #             print()
    #     except Exception as e:
    #         raise e


    def apply_settings(self):
        from calibre_plugins.interface_demo.config import prefs
        # In an actual non trivial plugin, you would probably need to
        # do something based on the settings in prefs
        prefs

