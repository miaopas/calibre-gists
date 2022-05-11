#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__copyright__ = '2011, Grant Drake <grant.drake@gmail.com>, 2017 additions by David Forrester <davidfor@internode.on.net>'
__docformat__ = 'restructuredtext en'
import xml.etree.ElementTree as ET
from calibre.ebooks.oeb.polish.container import get_container
from pathlib import Path
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

class QueueProgressDialogDeleteCreateby(QProgressDialog):

    def __init__(self, gui, book_ids, db):
        QProgressDialog.__init__(self, _('Working...'), _('Cancel'), 0, len(book_ids), gui)
        # QProgressDialog.__init__(self, _('Working...'), _('Cancel'), 0, len(book_ids))
        self.setWindowTitle(_('正在执行'))
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
            else:
                fmt = None

            if fmt:
                # db.save_original_format(book_id, fmt)
                epub_path = db.format_abspath(book_id, fmt)
                # with TemporaryDirectory('_modify-epub') as tdir:
                #     with CurrentDir(tdir):
                container = get_container(epub_path, tweak_mode=True)
                print(f'\n Temp path in {container.root} \n')

                # Find createby image
                creatby_image = None
                create_by_list = list(Path(container.root).glob('**/createby.png'))
                if len(create_by_list) > 1:
                    raise Exception('Found more then one createby.png')
                elif len(create_by_list) == 1:
                    create_by = create_by_list[0]
                    creatby_image = f'{create_by.parent.name}/{create_by.name}'
                    print(f'Found one createby  {creatby_image}')
                    db.save_original_format(book_id, fmt)
                    container.remove_item(f'{creatby_image}')
                    print(f'Removed {creatby_image}')
                    
                else:
                    # if no createby.png found, find a gif
                    gifs = list(Path(container.root).glob('**/*.gif'))
                    if len(gifs) > 1:
                        raise Exception('Found more then one gif!')
                    elif len(gifs)==1:
                        create_by = gifs[0]
                        creatby_image = f'{create_by.parent.name}/{create_by.name}'
                        print(f'Found one createby  {creatby_image}')
                        db.save_original_format(book_id, fmt)
                        container.remove_item(f'{creatby_image}')
                        print(f'Removed {creatby_image}')
                    else:
                        print('No Createby found.')
                    
                # If there are images removed, find the html and remove
                if creatby_image:
                    htmls =  sorted(list(Path(container.root).glob('**/*.html')) + list(Path(container.root).glob('**/*.xhtml')), reverse=True)
                    for html in htmls:
                        with open(html, 'r') as f:
                            contents = f.read()
                        if creatby_image in contents:
                            container.remove_item(f'{html.parent.name}/{html.name}')
                            break
                    print(f'Removed {html.name}')
                container.commit()

        except Exception as e:
            print(e)

        self.setValue(self.i)
        if self.i >= len(self.book_ids):
            self.gui = None
            return
        else:
            QTimer.singleShot(0, self.do_book)


