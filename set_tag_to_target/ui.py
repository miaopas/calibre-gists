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

    name = '设置标签'

    # Declare the main action associated with this plugin
    # The keyboard shortcut can be None if you dont want to use a keyboard
    # shortcut. Remember that currently calibre has no central management for
    # keyboard shortcuts, so try to use an unusual/unused shortcut.
    action_spec = ('设置标签', None,
            '设置标签', None)

    def genesis(self):
        
        icon = get_icons('images/icon.png')
        self.qaction.setIcon(icon)
        self.qaction.triggered.connect(self.action_update_tag_html)




    def get_book_ids(self):
        rows = self.gui.library_view.selectionModel().selectedRows()
        if not rows or len(rows) == 0:
            return error_dialog(self.gui, _('Cannot modify ePub'),
                _('You must select one or more books to perform this action.'), show=True)
        return self.gui.library_view.get_selected_ids()

    


    def action_update_tag_html(self):
        book_ids = self.get_book_ids()
        current_row=self.gui.library_view.currentIndex()
        target_id = self.gui.library_view.model().id(current_row)

        db = self.gui.current_db.new_api
        target_title = db.field_for("title", target_id)
        msg = QMessageBox()
        msg.setText(f'将已选择书籍标签设置为 {target_title} 的标签：')
        msg.setStandardButtons(QMessageBox.Ok  | QMessageBox.Cancel)
        ok = msg.button(QMessageBox.Ok)
        cancel = msg.button(QMessageBox.Cancel)
        # msg.buttonClicked.connect(lambda i: self.update_tags(i, ok, cancel))
        # raise Exception(target_title)
        msg.exec_()
        
        if msg.clickedButton() == ok:
            self.update_tag(book_ids, target_id)
        elif msg.clickedButton() == cancel:
            return
        else:
            raise Exception('PyQt Button Error happened')

    

    def update_tag(self, book_ids, target_id):
        db = self.gui.current_db.new_api
        target_tags = db.field_for("tags", target_id)
        

        for book_id in book_ids:
            db.set_field('tags', {book_id:target_tags})

        self.gui.library_view.model().refresh_ids(list(book_ids))
        self.gui.library_view.model().refresh_ids(list(book_ids),
                                      current_row=self.gui.library_view.currentIndex().row())
                        
            


    def apply_settings(self):
        from calibre_plugins.interface_demo.config import prefs
        # In an actual non trivial plugin, you would probably need to
        # do something based on the settings in prefs
        prefs

