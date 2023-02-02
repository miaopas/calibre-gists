#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__copyright__ = '2011, Grant Drake <grant.drake@gmail.com>, 2017 additions by David Forrester <davidfor@internode.on.net>'
__docformat__ = 'restructuredtext en'
import xml.etree.ElementTree as ET
from calibre.ebooks.oeb.polish.container import get_container
import os, traceback
from collections import OrderedDict
try:
    from PyQt5.Qt import QProgressDialog, QTimer
except ImportError:
    from PyQt4.Qt import QProgressDialog, QTimer

from calibre.gui2 import warning_dialog
try: # Needed as part of calibre conversion changes in 3.27.0.
    from calibre.ebooks.conversion.config import get_available_formats_for_book
except ImportError:
    from calibre.gui2.convert.single import get_available_formats_for_book
        
from calibre.utils.config import prefs

import calibre_plugins.count_pages.config as cfg

try:
    load_translations()
except NameError:
    pass # load_translations() added in calibre 1.9

class QueueProgressDialogUpdateDirection(QProgressDialog):

    def __init__(self, gui, book_ids, db):
        QProgressDialog.__init__(self, _('Working...'), _('Cancel'), 0, len(book_ids), gui)
        # QProgressDialog.__init__(self, _('Working...'), _('Cancel'), 0, len(book_ids))
        self.setWindowTitle(_('刷新翻页方向'))
        self.setMinimumWidth(500)
        self.book_ids, self.db = book_ids, db
        self.gui = gui

        self.i, self.books_to_scan = 0, []
        
        QTimer.singleShot(0, self.do_book)
        self.exec_()


    def do_book(self):
        book_id = self.book_ids[self.i]
        self.i += 1
        db =self.db
        try:
            print(f'Current on {db.field_for("title", book_id)}')
            title = db.field_for("title", book_id)
            print(f'Current on {title}')
            self.setLabelText(_('正在处理 ')+title)
            if db.has_format(book_id, 'AZW3'):
                fmt = 'AZW3'
            elif db.has_format(book_id, 'EPUB'):
                fmt = 'EPUB'
            # elif db.has_format(book_id, 'MOBI'):
            #     fmt = 'MOBI'
            else:
                fmt = None

            if fmt:
                epub_path = db.format_abspath(book_id, fmt)
                try:
                    container = get_container(epub_path, tweak_mode=True)
                except Exception as e:
                    raise Exception(str(e) + str(book_id))

                path = container.opf_dir + '/' + container.opf_name.split('/')[-1]
                

                print(f'container.opf_dir :  {container.opf_dir}')
                print(f'container.opf_name : {container.opf_name}')

                tree = ET.parse(path)
                root = tree.getroot()
                page_turn_mi = None
                for ele in list(root):
                    if 'spine' in ele.tag:
                        if ele.attrib.get('page-progression-direction') is None or ele.attrib['page-progression-direction'] != 'rtl':
                            page_turn_mi =  'L to R'
                        elif ele.attrib['page-progression-direction'] == 'rtl':
                            page_turn_mi =  'R to L'
                
                db.set_field('#page_turn_direction', {book_id: page_turn_mi})

                print("finished writing to columns")
                print()
        except Exception as e:
            raise e

        # self.gui.library_view.selectionModel().clearSelection()
        self.setValue(self.i)
        if self.i >= len(self.book_ids):
            self.gui = None
            return
        else:
            QTimer.singleShot(0, self.do_book)


class QueueProgressDialogChangeDirection(QProgressDialog):

    def __init__(self, gui, book_ids, db):
        QProgressDialog.__init__(self, _('Working...'), _('Cancel'), 0, len(book_ids), gui)
        self.setWindowTitle(_('切换翻页方向'))
        self.setMinimumWidth(500)
        self.book_ids, self.db = book_ids, db
        self.gui = gui

        self.i, self.books_to_scan = 0, []
        
        QTimer.singleShot(0, self.do_book)
        self.exec_()


    def do_book(self):
        book_id = self.book_ids[self.i]
        self.i += 1
        db =self.db
        title = db.field_for("title", book_id)
        print(f'Current on {title}')
        self.setLabelText(_('正在处理 ')+title)
        if db.has_format(book_id, 'AZW3'):
            fmt = 'AZW3'
        elif db.has_format(book_id, 'EPUB'):
            fmt = 'EPUB'
        else:
            fmt = None

        if fmt:
            db.save_original_format(book_id, fmt)
            epub_path = db.format_abspath(book_id, fmt)
            # with TemporaryDirectory('_modify-epub') as tdir:
            #     with CurrentDir(tdir):
            container = get_container(epub_path, tweak_mode=True)
            path = container.opf_dir + '/' + container.opf_name
            print(path)
            tree = ET.parse(path)
            root = tree.getroot()
            # Change the opf file itself
            for ele in list(root):
                if 'spine' in ele.tag:
                    if ele.attrib.get('page-progression-direction') is None or ele.attrib['page-progression-direction'] != 'rtl':
                        ele.attrib['page-progression-direction'] = 'rtl'
                    elif ele.attrib['page-progression-direction'] == 'rtl':
                        del ele.attrib['page-progression-direction']
    
            tree._setroot(root)
            tree.write(path)
            # commit the changes
            container.commit()
            print("finished edit books")        

        self.setValue(self.i)
        if self.i >= len(self.book_ids):
            return
        else:
            QTimer.singleShot(0, self.do_book)