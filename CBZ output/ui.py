import imp
from calibre.gui2.convert import Widget
from PyQt5 import QtCore, QtWidgets, uic
from pathlib import Path
from calibre import CurrentDir
import os
import io

from calibre_plugins.cbz_output.cbz_output_ui import Ui_Form

option = (
    'no_crop',
    'starting_page',
    'starting_page_left_crop',
    'starting_page_right_crop',
    'starting_page_up_crop',
    'starting_page_down_crop',
    'next_page_left_crop',
    'next_page_right_crop',
    'next_page_up_crop',
    'next_page_down_crop'
)

class PluginWidget(Widget, Ui_Form):
    TITLE = "CBZ 输出"
    HELP = ""
    COMMIT_NAME = "CBZ_output"
    # ICON = I('mimetypes/txt.png')

    def __init__(self, parent, get_option, get_help, db=None, book_id=None):
        Widget.__init__(self, parent, option)

        self.db, self.book_id = db, book_id
        self.initialize_options(get_option, get_help, db, book_id)
        self.opt_no_crop.toggle()
        self.opt_no_crop.toggle()
