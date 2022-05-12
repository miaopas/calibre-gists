#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai


__license__   = 'GPL v3'
__copyright__ = '2011, Kovid Goyal <kovid@kovidgoyal.net>'
__docformat__ = 'restructuredtext en'

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

    name = 'Top'

    # Declare the main action associated with this plugin
    # The keyboard shortcut can be None if you dont want to use a keyboard
    # shortcut. Remember that currently calibre has no central management for
    # keyboard shortcuts, so try to use an unusual/unused shortcut.
    # Create our top-level menu/toolbar action (text, icon_path, tooltip, keyboard shortcut)
    action_spec = ('Top', None,
            'Scroll to top', ())

    def genesis(self):
        icon = get_icons('images/icon.png')
        self.qaction.setIcon(icon)
        self.qaction.triggered.connect(self.action_scroll_to_top)


    def action_scroll_to_top(self):
        self.gui.library_view.selectRow(0)
        self.gui.library_view.selectionModel().reset()
        
        

