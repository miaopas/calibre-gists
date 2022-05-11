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

    name = '更新标签'

    # Declare the main action associated with this plugin
    # The keyboard shortcut can be None if you dont want to use a keyboard
    # shortcut. Remember that currently calibre has no central management for
    # keyboard shortcuts, so try to use an unusual/unused shortcut.
    action_spec = ('更新标签', None,
            '更新标签', None)

    def genesis(self):
        
        icon = get_icons('images/icon.png')
        self.qaction.setIcon(icon)
        self.qaction.triggered.connect(self.action_update_tag_html)




    def get_book_ids(self):
        rows = self.gui.library_view.selectionModel().selectedRows()
        if not rows or len(rows) == 0:
            return error_dialog(self.gui, _('Cannot modify ePub'),
                _('You must select one or more books to perform this action.'), show=True)
        return set(self.gui.library_view.get_selected_ids())


    def action_update_tag_html(self):
        book_ids = self.get_book_ids()
        print(book_ids)
        
        self.update_tag_html(book_ids)

    def update_tag_html(self, book_ids):
        
        db = self.gui.current_db.new_api
        for book_id in book_ids:
            mi = db.get_metadata(book_id)
            tags_mi = mi.metadata_for_field('tags')

            tags = db.field_for("tags", book_id)
            class Tags:
                def __init__(self, name, child_name, parent_name, depth):
                    self.name = name
                    self.child_name = []
                    self.child_name.append(child_name)
                    self.parent_name = parent_name
                    self.depth = depth
                def __repr__(self):
                    return str(f'Parent:{self.parent_name} \t\n Child: {self.child_name}\n {self.depth}')

                def add_child(self, child_name):
                    if child_name not in self.child_name:
                        self.child_name.append(child_name)

                # def add_parent(self, parent_name):
                #     if parent_name not in self.parent_name:
                #         self.parent_name.append(parent_name)
                

            # tags = ('1 主题.百合', '1 主题.日常.职场', '2 元素.恋爱.掰弯', '2 元素.恋爱.少女爱', '3 设定.地点.日本', '3 设定.篇幅.短篇', '4 主要人物.A 年龄段.成年', '4 主要人物.B 外观.黑长直', '4 主要人物.C 属性.直女', '4 主要人物.D 职业.OL')
            tag_dict = {}
            for tag in sorted(tags):
                splited = list(map(lambda x:x.split(' ')[-1],tag.split('.')))
                
                for i,tag in enumerate(splited):
                    child = None
                    parent = None
                    
                    if i>=1:
                        parent = splited[i-1]

                    try:
                        child = splited[i+1]
                    except IndexError:
                        pass

                    if not tag_dict.get(tag):
                        tag_dict[tag] = Tags(tag, child,parent,i)
                    else:
                        tag_dict[tag].add_child(child)
                        # tag_dict[tag].add_parent(parent)
            # Root tags
            main_tags = []
            for tag in tag_dict:
                if tag_dict[tag].parent_name is None:
                    main_tags.append(tag)

            def build_from_tag(tag, in_html):
                html = []
                def build_from_tag(tag):
                    if len(tag_dict[tag].child_name) == 1 and (None in tag_dict[tag].child_name):
                        html.append('&nbsp;'*3* tag_dict[tag].depth + tag +'<br>')
                        return
                    else:
                        if tag in main_tags:
                            pass
                            # html = html + '&nbsp;'*2* tag_dict[tag].depth + f'{tag}' + '<br>'
                        else: 
                            html.append('<span style="color: #286aff">' + '&nbsp;'*3* tag_dict[tag].depth +tag + '</span>' + '<br>')
                        for child in tag_dict[tag].child_name:
                            if child is not None:
                                build_from_tag(child)
                build_from_tag(tag)
                return in_html+''.join(html)

            htmls = []
            for main_tag in main_tags:
                # Add heading
                html = f'<h3>{main_tag}</h3><p>'
                # add contents
                html = build_from_tag(main_tag, html)
                html = html + '</p>'
                htmls.append(html)

            left_col = ''.join(htmls[::2])+ '&nbsp;'*100+'<br>'
            right_col = ''.join(htmls[1::2])+ '&nbsp;'*100+'<br>'
            output_html = f"""<table style="border-collapse: collapse; width: 100%;" border="0">
            <tbody>
            <tr>
            <td style="width: 50%;"><br>{left_col}</td>
            <td style="width: 50%;"><br>{right_col}</td>
            </tr>
            </tbody>
            </table>"""
            # mi = db.get_metadata(book_id)
            # tags_html_mi = mi.metadata_for_field('#tag_html')
            # tags_html_mi['#value#'] =  output_html
            # mi.set_user_metadata("#tag_html", tags_html_mi)
            # db.set_metadata(book_id, mi)
            db.set_field("#tag_html", {book_id:output_html })
        self.gui.library_view.model().refresh_ids(list(book_ids))
        self.gui.library_view.model().refresh_ids(list(book_ids),
                                      current_row=self.gui.library_view.currentIndex().row())
                        
            


    def apply_settings(self):
        from calibre_plugins.interface_demo.config import prefs
        # In an actual non trivial plugin, you would probably need to
        # do something based on the settings in prefs
        prefs

