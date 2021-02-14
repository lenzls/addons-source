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

# TODO: loading spinner
# TODO: add scrolling
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
        print("In build tree")

    def build_widget(self):
        """
        Builds the container widget for the main view pane. Must be overridden
        by the base class. Returns a gtk container widget.
        """
        self.tree = Gtk.TreeView(model=Gtk.TreeStore(str, str))
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Title", renderer, text=0, background=1)
        self.tree.append_column(column)

        print("starting coroutine")
        import threading
        b = threading.Thread(target=self.file_file_system_model, args=(self.dbstate.db.get_mediapath(), self.get_list_of_media_paths_in_db()))
        b.start()
        print("started coroutine")
        
        return self.tree
        
    def file_file_system_model(self, media_path, media_paths_in_db):
        print("start filling mode")

        store = Gtk.TreeStore(str, str)
        if media_path is None:
            WarningDialog(
                _("Media path not set"),
                _('Media path not set. You must set the "Base path for relative media paths" in the Preferences.'),
                parent=self.uistate.window
            )
            return

        parents = {}
        for dir, dirs, files in os.walk(media_path):
            for subdir in dirs:
                parents[os.path.join(dir, subdir)] = store.append(parents.get(dir, None), [subdir, 'orange'])
            for item in files:
                if item in media_paths_in_db:
                    color = 'green'
                else:
                    color = 'red'

                store.append(parents.get(dir, None), [item, color])
        
        self.tree.set_model(store)

        print("stop filling mode")

    def get_list_of_media_paths_in_db(self):
        media_paths = set()
        for handle in self.dbstate.db.get_media_handles():
            media = self.dbstate.db.get_media_from_handle(handle)
            media_paths.add(media.get_path())
        return media_paths
