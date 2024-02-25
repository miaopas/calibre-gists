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
from calibre.gui2 import error_dialog, question_dialog
from calibre.gui2.my_customised import JumpToFolderBox
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

from subprocess import Popen, PIPE, STDOUT
import sys
import re
def calibreWrapper(cmd):
    process = Popen(cmd, stdout=PIPE, stderr=STDOUT)

    # Poll process for new output until finished
    while True:
        nextline = process.stdout.readline()
        if nextline == b'' and process.poll() is not None:
            break
        x = re.findall("[0-9]{2}.[0-9]{2}%", output)
        if len(x)==1:
            percent = x[0]
            self.setLabelText(f'正在处理 {input_path.name : >2}  {percent: >2}')
            self.setValue(self.progress + int(float(percent[:-1])))
        
        sys.stdout.write(nextline.decode('utf-8'))
        sys.stdout.flush()
        

    output = process.communicate()[0]
    exitCode = process.returncode
    print(exitCode, output)
    if (exitCode == 0):
        return output
    else:
        pass


class QueueProgressDialogUpdateDirection(QProgressDialog):

    def __init__(self, gui, book_id, db):
        self.book_id, self.db = book_id, db
        self.gui = gui

        self.i, self.images_to_do = 0, []
        self.progress = 0
        self.do_book()


    def process_image(self, input_path):
        import re
        import subprocess
        from PIL import Image
        import os
        output_path = input_path

        # print('------------------------------')
        # print(get_resources('realesrgan-ncnn-vulkan').decode)
        cmd = ['/Users/haruka/Calibre Extra Files/realesrgan-ncnn-vulkan', '-i', input_path, '-o', output_path, '-n', 'realesrgan-x4plus-anime']
        def calibreWrapper(cmd):
            process = Popen(cmd, stdout=PIPE, stderr=STDOUT)

            # Poll process for new output until finished
            while True:
                nextline = process.stdout.readline()
                if nextline == b'' and process.poll() is not None:
                    break
                output = nextline.decode('utf-8')
                x = re.findall("[0-9]{2}.[0-9]{2}%", output)
                if len(x)==1:
                    percent = x[0]
                    self.setLabelText(f'正在处理 {input_path.name : >2}  {percent: >2}')
                    self.setValue(self.progress + int(float(percent[:-1])))
                
                sys.stdout.write(nextline.decode('utf-8'))
                sys.stdout.flush()

        # def run_command(command):
        #     print('inside run command')
        #     process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr = subprocess.STDOUT, shell=True)
            
        #     for line in iter(process.stdout.readline, b''):
        #         output = line.decode("utf-8").replace('\n','')
        #         print(output)
        #         x = re.findall("[0-9]{2}.[0-9]{2}%", output)
        #         if len(x)==1:
        #             percent = x[0]
        #             self.setLabelText(f'正在处理 {input_path.name : >2}  {percent: >2}')
        #             self.setValue(self.progress + int(float(percent[:-1])))

        #     process.stdout.close()
        #     process.wait()

        print(f'Begin processing {input_path}')
        im = Image.open(input_path)
        original_size = im.size
        print(f'Image size: {original_size}')
        minimum_width = 2048
        if original_size[0]<minimum_width:
            original_size = (minimum_width, int(minimum_width*original_size[1]/original_size[0]))

            print(f'Too small, reshape to size: {original_size}')

        print(f'Begin upsampling')
        # upsamping
        calibreWrapper(cmd)
        # run_command(cmd)
        im = Image.open(output_path)
        im = im.resize(original_size, resample=Image.LANCZOS)
        im.save(output_path)

    def do_page(self):
        image_path = self.images_to_do[self.i]
        self.i += 1
        
        try:
            print(f'Current on {image_path.name}')
            self.process_image(image_path)

        except Exception as e:
            raise e

        self.progress = self.i*100
        self.setValue(self.progress)

        if self.i >= len(self.images_to_do):
            self.gui = None
            return
        else:
            QTimer.singleShot(0, self.do_page)

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
        db =self.db
        title = db.field_for("title", self.book_id)
        print(f'Current on {title}')
    
        if db.has_format(self.book_id, 'AZW3'):
            fmt = 'AZW3'
        elif db.has_format(self.book_id, 'EPUB'):
            fmt = 'EPUB'
        else:
            fmt = None

        if fmt:
            
            epub_path = db.format_abspath(self.book_id, fmt)
            print(f'Book Path: {epub_path}')
            # Backup original file
            self.back_up_file(epub_path)
    

            container = get_container(epub_path, tweak_mode=True)
            book_path = container.opf_dir
            print(f'!!!!!!Container Path: {book_path}')
            # from pathlib import Path
            # images = []
            # types = ('*.jpg', '*.JPG', '*.PNG', '*.png', '*.jpeg', '*.JPEG', 
            # '*.tiff', '*.GIF',  '*.gif') # the tuple of file types
            # for ext in types:
            #     images.extend(Path(book_path).rglob(ext))
            # print(f'Totally {len(images)} images')

            # if len(images) == 0:
            #     return None
            # self.images_to_do = sorted(images)
            # # self.images_to_do = images

            # print('here')

            # QProgressDialog.__init__(self, _('Working...'), _('Cancel'), 0, len(images)*100, self.gui)
            # self.setWindowTitle(_('提升画质'))
            # self.setMinimumWidth(500)
             
            # QTimer.singleShot(0, self.do_page)
            # self.exec_()
            print(f'File size {os.path.getsize(book_path)}')
            if JumpToFolderBox(JumpToFolderBox.QUESTION, '请处理图片', f'书籍已解压, 请处理图片后继续', f'{book_path}', parent=self.gui,
                   show_copy_button=True, default_yes=True,
                   q_icon=None, yes_text='继续', no_text='取消',
                   yes_icon=None, no_icon=None, add_abort_button=False):
                container.commit()
                print(f'File size {os.path.getsize(book_path)}')
            # db.format_metadata(self.book_id, fmt, update_db=True, commit=True)