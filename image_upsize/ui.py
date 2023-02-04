#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai


__license__   = 'GPL v3'
__copyright__ = '2011, Kovid Goyal <kovid@kovidgoyal.net>'
__docformat__ = 'restructuredtext en'
from qt.core import QDialog, QVBoxLayout, QPushButton, QMessageBox, QLabel
from calibre.gui2 import error_dialog, info_dialog
from calibre.utils.logging import Log
from calibre.libunzip import extract as zipextract
from calibre.ptempfile import TemporaryDirectory
from calibre import CurrentDir, guess_type
from calibre_plugins.image_upscale.dialogs import QueueProgressDialogUpdateDirection
from calibre.ebooks.oeb.polish.container import get_container
from pathlib import Path
from calibre.gui2.my_customised import JumpToFolderBox

import xml.etree.ElementTree as ET
try:
    from PyQt5.Qt import QToolButton, QMenu
except ImportError:
    from PyQt4.Qt import QToolButton, QMenu
import glob
if False:
    # This is here to keep my python error checker from complaining about
    # the builtin functions that will be defined by the plugin loading system
    # You do not need this code in your plugins
    get_icons = get_resources = None

# The class that all interface action plugins must inherit from
from calibre.gui2.actions import InterfaceAction


class InterfacePlugin(InterfaceAction):

    name = '提升图片清晰度'

    # Declare the main action associated with this plugin
    # The keyboard shortcut can be None if you dont want to use a keyboard
    # shortcut. Remember that currently calibre has no central management for
    # keyboard shortcuts, so try to use an unusual/unused shortcut.
    action_spec = ('提升图片清晰度', None,
            '提升图片清晰度', None)

    def genesis(self):
        
        icon = get_icons('images/icon.png')
        self.qaction.setIcon(icon)
        self.qaction.triggered.connect(self.action_image_upscale_azw)

        # self.create_menu_action(self.menu, "处理AZW", "处理AZW", icon=None,
        # description="直接处理 AZW 或 Epub", triggered=self.action_change_turn_direction)
        # self.menu.aboutToShow.connect(self.about_to_show_menu)


    def get_book_id(self):
        rows = self.gui.library_view.selectionModel().selectedRows()
        if not rows or (not len(rows) == 1):
            error_dialog(self.gui, _('Cannot modify ePub'), _('You must select only one book to perform this action.'), show=True)
            return None
        return list(self.gui.library_view.get_selected_ids())[0]


    def action_image_upscale_azw(self):

        book_id = self.get_book_id()
        print(book_id)
        if not book_id:
            return 
        db = self.gui.current_db.new_api
        self.book_id = book_id
        if self.do_book():
            self.gui.library_view.model().refresh_ids([book_id])
            self.gui.library_view.model().refresh_ids([book_id],
                                        current_row=self.gui.library_view.currentIndex().row())
            d = info_dialog(self.gui, '完成', '完成', det_msg='', show=False,
            show_copy_button=False, only_copy_details=False)
            d.exec()
        

    # def update_turn_direction_column(self, book_id):
        
    #     db = self.gui.current_db.new_api
    #     self.book_id = book_id
    #     self.do_book()
       
    #     # d = QueueProgressDialogUpdateDirection(self.gui, book_id, db)
    #     # d.show()
    #     # if d.wasCanceled():
    #     #     return 

    #     # self.gui.library_view.selectionModel().clearSelection()
        


    def back_up_file(self, book_path):
        from pathlib import Path
        p = Path(book_path)
        bk_file_name = p.name + '.bk'
        bk_file_path = p.parent / Path(bk_file_name)
        if bk_file_path.exists():
            print('Backup already exists')
        else:
            import shutil
            shutil.copy(book_path, bk_file_path)
            print('Backup successful')

    def do_book(self):
        db =self.gui.current_db.new_api
        title = db.field_for("title", self.book_id)
        print(f'Current on {title}')
        from calibre.gui2.dialogs.choose_format import ChooseFormatDialog

        valid_fmts = set({'EPUB', 'AZW3', 'CBZ'})
        fmt = set(db.formats(self.book_id, verify_formats=True))
        fmt = fmt & valid_fmts
        d = ChooseFormatDialog(self.gui, '选择格式', fmt)
        if d.exec() != QDialog.DialogCode.Accepted or not d.format():
            return
        fmt = d.format()

        icon = get_icons('images/icon.png')
        if fmt in set({'EPUB', 'AZW3'}):
            epub_path = db.format_abspath(self.book_id, fmt)
            print(f'Book Path: {epub_path}')
            # Backup original file
            self.back_up_file(epub_path)
            container = get_container(epub_path, tweak_mode=True)
            book_path = container.opf_dir
            print(f'Container Path: {book_path}')
            
            d = JumpToFolderBox(JumpToFolderBox.QUESTION, '请处理图片', f'书籍已解压, 请处理图片后继续', f'{container.opf_dir}', parent=self.gui,
                   show_copy_button=True, default_yes=True,
                   q_icon=icon, yes_text='继续', no_text='取消',
                   yes_icon=None, no_icon=None, add_abort_button=False)

            ret = d.exec() == QDialog.DialogCode.Accepted
            
            if ret:
                container.commit()
                return True
            else:
                return False
        elif fmt == 'CBZ':
            book_path = db.format_abspath(self.book_id, fmt)
            print(f'Book Path: { book_path}')
            self.back_up_file(book_path)
            book_dir = Path(book_path).parent
            
            from calibre.utils import zipfile
            zfile = zipfile.ZipFile(book_path, "r")

            with TemporaryDirectory('_cbz_extract') as tdir:
                print(f'Working in {tdir}')
                with CurrentDir(tdir):
                    extract_dir = Path(tdir) / Path(book_path).stem

                    zfile.extractall(path=str(extract_dir))

                    d = JumpToFolderBox(JumpToFolderBox.QUESTION, '请处理图片', f'书籍已解压, 请处理图片后继续', f'{str(extract_dir)}', parent=self.gui,
                        show_copy_button=True, default_yes=True,
                        q_icon=icon, yes_text='继续', no_text='取消',
                        yes_icon=None, no_icon=None, add_abort_button=False)

                    ret = d.exec() == QDialog.DialogCode.Accepted

                    if ret:
                        # Delete the book and then recreate
                        tbook_path = Path(tdir) / Path(book_path).name
                        zfile = zipfile.ZipFile(str(tbook_path), "w")
                        zfile.add_dir(str(extract_dir))
                        zfile.close()
                        db.add_format(self.book_id, 'cbz', str(tbook_path), True, False)
                        return True
                    else:
                        return False

    def apply_settings(self):
        from calibre_plugins.interface_demo.config import prefs
        # In an actual non trivial plugin, you would probably need to
        # do something based on the settings in prefs
        prefs