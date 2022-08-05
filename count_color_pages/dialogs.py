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
from calibre import CurrentDir
from pathlib import Path
from PIL import Image, ImageStat
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

def get_files(path, extensions):
    all_files = []
    for ext in extensions:
        all_files.extend(Path(path).glob(f'**/{ext}'))
    return all_files

def is_color(path):
    im = Image.open(path).convert("RGB")
    stat = ImageStat.Stat(im).sum
    try:
        test = [i/(max(stat)) for i in stat]
        if test[0]>0.975 and test[1]>0.975 and test[2]>0.975:
            return False
        else:
            return True
    except Exception as e:
        print(f'{path} raised an exception: {e}')
        return False

class QueueProgressDialogCountColorPages(QProgressDialog):

    def __init__(self, gui, book_ids, db):
        QProgressDialog.__init__(self, _('Working...'), _('Cancel'), 0, len(book_ids), gui)
        # QProgressDialog.__init__(self, _('Working...'), _('Cancel'), 0, len(book_ids))
        self.setWindowTitle(_('获取彩页数量'))
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
            title = db.field_for("title", book_id)
            print(f'Current on {title}')
            self.setLabelText(_('正在处理 ')+title)
            
            if db.has_format(book_id, 'EPUB'):
                fmt = 'EPUB'
            elif db.has_format(book_id, 'AZW3'):
                fmt = 'AZW3'
            else:
                fmt = None

            if fmt:
                epub_path = db.format_abspath(book_id, fmt)
                try:
                    container = get_container(epub_path, tweak_mode=False)
                except Exception as e:
                    raise Exception(str(e) + str(book_id))

                res = 0
                images = get_files(container.root,('*.png', '*.jpeg', '*.jpg', '*.gif'))
                for path in sorted(images):
                    if is_color(path):
                        res += 1

                
                db.set_field('#color_page', {book_id: res})
                # print(f"finished writing to columns for {book_id}")
        except Exception as e:
            raise e

        # self.gui.library_view.selectionModel().clearSelection()
        self.setValue(self.i)
        if self.i >= len(self.book_ids):
            self.gui = None
            return
        else:
            QTimer.singleShot(0, self.do_book)
