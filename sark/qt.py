import os
import sys

import idaapi

from . import exceptions

# This nasty piece of code is here to force the loading of IDA's PySide.
# Without it, Python attempts to load PySide from the site-packages directory,
# and failing, as it does not play nicely with IDA.
old_path = sys.path[:]
try:
    ida_python_path = os.path.dirname(idaapi.__file__)
    sys.path.insert(0, ida_python_path)
    from PySide import QtGui, QtCore
finally:
    sys.path = old_path


def capture_widget(widget, path):
    """Grab an image of a Qt widget and save to file."""
    pixmap = QtGui.QPixmap.grabWidget(widget)
    pixmap.save(path)


def get_widget(title):
    """Get the Qt widget of the IDA window with the given title."""
    tform = idaapi.find_tform(title)
    if not tform:
        return

    return idaapi.PluginForm.FormToPySideWidget(tform)


def resize_widget(widget, width, height):
    """Resize a Qt widget."""
    widget.setGeometry(0, 0, width, height)


def get_window():
    """Get IDA's top level window."""
    tform = idaapi.get_current_tform()
    widget = idaapi.PluginForm.FormToPySideWidget(tform)
    window = widget.window()
    return window


class MenuManager(object):
    """IDA Menu Manipulation

    Use this class to add your own top-level menus.
    While this is discouraged by the SDK:

    > You should not change top level menu, or the Edit,Plugins submenus

    (documentation for `attach_action_to_menu`, kernwin.hpp)

    Adding top-level menus is useful sometimes.
    Nonetheless, you should be careful and make sure to remove all your menus
    when you are done. Leaving them handing would force users to restart IDA
    to remove them.

    Usage of this class should be as follows:

    >>> # Use the manager to add top-level menus
    >>> menu_manager = MenuManager()
    >>> menu_manager.add_menu("MyMenu")
    >>> # Use the standard API to add menu items
    >>> idaapi.attach_action_to_menu("MyMenu/", "SomeActionName", idaapi.SETMENU_APP)
    >>> # When a menu is not needed, remove it
    >>> menu_manager.remove_menu("MyMenu")
    >>> # When you are done with the manager (and want to remove all menus you added.)
    >>> # clear it before deleting.
    >>> menu_manager.clear()
    """

    def __init__(self):
        super(MenuManager, self).__init__()

        self._window = get_window()
        self._menu = self._window.findChild(QtGui.QMenuBar)

        self._menus = {}

    def add_menu(self, name):
        """Add a top-level menu.

        The menu manager only allows one menu of the same name. However, it does
        not make sure that there are no pre-existing menus of that name.
        """
        if name in self._menus:
            raise exceptions.MenuAlreadyExists("Menu name {!r} already exists.".format(name))
        menu = self._menu.addMenu(name)
        self._menus[name] = menu

    def remove_menu(self, name):
        """Remove a top-level menu.

        Only removes menus created by the same menu manager.
        """
        if name not in self._menus:
            raise exceptions.MenuNotFound(
                "Menu {!r} was not found. It might be deleted, or belong to another menu manager.".format(name))

        self._menu.removeAction(self._menus[name].menuAction())

    def clear(self):
        """Clear all menus created by this manager."""
        for menu in self._menus.itervalues():
            self._menu.removeAction(menu.menuAction())


