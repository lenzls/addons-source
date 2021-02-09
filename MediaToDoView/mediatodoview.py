import os

from gramps.gui.views.pageview import PageView
from gramps.gui.dialog import WarningDialog
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gi.repository import Gtk


try:
    _trans = glocale.get_addon_translator(__file__)
except ValueError:
    _trans = glocale.translation

_ = _trans.gettext


class MediaToDoView(PageView):

    def __init__(self, pdata, dbstate, uistate):
        PageView.__init__(self, _('Media ToDo'), pdata, dbstate, uistate)
        self.dbstate = dbstate
        self.uistate = uistate

    def build_tree(self):
        """
        Rebuilds the current display. This must be overridden by the derived
        class.

        This is called by the parent class when the view becomes visible. Since
        all handling of visibility is now in rebuild, see that for more
        information.
        """
        pass

    def build_widget(self):
        """
        Builds the container widget for the main view pane. Must be overridden
        by the base class. Returns a gtk container widget.
        """
        tree = Gtk.TreeView(model=self.create_file_system_model())
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Title", renderer, text=0)
        tree.append_column(column)
        return tree
        

    def create_file_system_model(self):
        media_path = self.dbstate.db.get_mediapath()
        if media_path is None:
            WarningDialog(
                _("Media path not set"),
                _('Media path not set. You must set the "Base path for relative media paths" in the Preferences.'),
                parent=self.uistate.window
            )
            return

        store = Gtk.TreeStore(str)
        
        parents = {}
        for dir, dirs, files in os.walk(media_path):
            for subdir in dirs:
                parents[os.path.join(dir, subdir)] = store.append(parents.get(dir, None), [subdir])
            for item in files:
                store.append(parents.get(dir, None), [item])
        return store
