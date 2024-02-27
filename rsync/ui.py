#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai


__license__   = 'GPL v3'
__copyright__ = '2011, Kovid Goyal <kovid@kovidgoyal.net>'
__docformat__ = 'restructuredtext en'
from qt.core import QDialog, QVBoxLayout, QPushButton, QMessageBox, QLabel
from calibre.gui2 import error_dialog, info_dialog, question_dialog
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


def do_sync(*args, **kwargs):
    
    kwargs['notification'](0.01, 'Syncing')
    import subprocess
    cmd = "/opt/homebrew/bin/rsync --archive --verbose --compress --delete -e ssh --stats /Volumes/SSD\ Drive/Calibre\ Library/Library/ haruka@192.168.1.233:/var/services/homes/harukaWebDAV/CalibreLibrary/Main\ Library/"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    return result.stdout

def parse_rsync_output(output):
        import re
        # Regular expressions to extract information
        transferred_regex = re.compile(r'Number of regular files transferred: (\d+)')
        deleted_regex = re.compile(r'Number of deleted files: (\d+)')
        new_files_regex = re.compile(r'Number of created files: (\d+)')
        total_size_regex = re.compile(r'Total transferred file size: ([\d,]+) bytes')

        # Search for matches in the output
        transferred_match = transferred_regex.search(output)
        deleted_match = deleted_regex.search(output)
        new_files_match = new_files_regex.search(output)
        total_size_match = total_size_regex.search(output)

        # Extract information from matches
        transferred = int(transferred_match.group(1)) if transferred_match else None
        deleted = int(deleted_match.group(1)) if deleted_match else None
        new_files = int(new_files_match.group(1)) if new_files_match else None
        total_size = round(int(total_size_match.group(1).replace(',', ''))/ 1048576,4) if total_size_match else None

        # Return extracted information
        return {
            "transferred": transferred,
            "deleted": deleted,
            "new_files": new_files,
            "total_size": total_size
        }
    
class InterfacePlugin(InterfaceAction):

    name = 'Sync'

    # Declare the main action associated with this plugin
    # The keyboard shortcut can be None if you dont want to use a keyboard
    # shortcut. Remember that currently calibre has no central management for
    # keyboard shortcuts, so try to use an unusual/unused shortcut.
    action_spec = ('Sync', None,
            'Sync', None)

    def genesis(self):
        icon = get_icons('images/icon.png')
        self.qaction.setIcon(icon)
        self.qaction.triggered.connect(self.toolbar_triggered)

    def toolbar_triggered(self):
        

        func = 'arbitrary_n'

        args = ['calibre_plugins.rsync.ui', 'do_sync', []]


        desc = 'Sync library to NAS'
        self.gui.job_manager.run_job(
                self.Dispatcher(self._completed), func, args=args,
                    description=desc)
        
        self.gui.status_bar.show_message('Syncing library to NAS' )

    

    def _proceed(self, payload):
        # info = parse_rsync_output(payload)
        # output = f"""Transferred files:  {info["transferred"]}\nTotal size (MB): {info['total_size']} MB"""

        # info_dialog(self.gui, 'Sync Results', output, det_msg=payload, show=True)
        pass
    

    def _completed(self, job):
        if job.failed:
            return self.gui.job_exception(job, dialog_title=_('Failed'))

        self.gui.status_bar.show_message('Syncing completed', 3000)

        info = parse_rsync_output(job.result)
        output = f"""Transferred files:  {info["transferred"]}\nTotal size (MB): {info['total_size']} MB"""

        self.gui.proceed_question(self._proceed,
                        job.result, job.result,
                        'RSync log', 'Sync complete', output,
                        show_copy_button=False, show_ok=True,  icon = get_icons('images/ok.png'))
    # def sync(self):
    #     import subprocess
    #     cmd = "/opt/homebrew/bin/rsync --archive --verbose --compress --delete -e ssh --dry-run --stats /Volumes/SSD\ Drive/Calibre\ Library/Library/ haruka@192.168.1.233:/var/services/homes/harukaWebDAV/CalibreLibrary/Main\ Library/"
    #     result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    #     info = self.parse_rsync_output(result.stdout)

    #     output = f"""Transferred files:  {info["transferred"]}\nTotal size (MB): {info['total_size']} MB\n\n\t开始同步？"""

    #     if question_dialog(self.gui,'同步',output, det_msg=result.stdout):
    #         cmd = "/opt/homebrew/bin/rsync --archive --verbose --compress --delete -e ssh --stats /Volumes/SSD\ Drive/Calibre\ Library/Library/ haruka@192.168.1.233:/var/services/homes/harukaWebDAV/CalibreLibrary/Main\ Library/"
    #         result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    #         info = self.parse_rsync_output(result.stdout)
    #         output = f"""Transferred files:  {info["transferred"]}\nTotal size (MB): {info['total_size']} MB"""
    #         d = info_dialog(self.gui, '结果', output, det_msg=result.stdout, show_copy_button=False)
    #         d.exec()



        


    def apply_settings(self):
        from calibre_plugins.interface_demo.config import prefs
        # In an actual non trivial plugin, you would probably need to
        # do something based on the settings in prefs
        prefs

