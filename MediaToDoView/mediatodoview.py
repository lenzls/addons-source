from enum import Enum
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

class PATH_STATE(Enum):
    IGNORED = 0 # empty dirs
    NOT_IN_DB = 1   # for folders this means that no child is in DB
    PARTIALLY_IN_DB = 2 # for folders this means that some children are in DB. For files this does not make sense
    FULLY_IN_DB = 3 # for folders this means that all children are in DB

COLOR_MAPPING = {
    PATH_STATE.IGNORED: 'grey',
    PATH_STATE.NOT_IN_DB: 'red',
    PATH_STATE.PARTIALLY_IN_DB: 'yellow',
    PATH_STATE.FULLY_IN_DB: 'green',
}

# TODO: Improve colors
# TODO: try out progress bar
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
        self.container = Gtk.ScrolledWindow()
        progress_bar_container = Gtk.Layout()
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_show_text(True)
        self.progress_bar.set_text("Hello")
        self.progress_bar.set_pulse_step(0.01)
        progress_bar_container.add(self.progress_bar)
        self.container.add(progress_bar_container)

        self.tree = Gtk.TreeView(model=Gtk.TreeStore(str, str))
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Title", renderer, text=0, background=1)
        self.tree.append_column(column)

        print("starting coroutine")
        import threading
        b = threading.Thread(target=self.create_model_and_replace_progress_bar, args=(self.dbstate.db.get_mediapath(), self.get_list_of_media_paths_in_db()))
        b.start()
        print("started coroutine")
        
        return self.container

    def create_model_and_replace_progress_bar(self, media_path, media_paths_in_db):
        store = self.create_model(media_path, media_paths_in_db)
        self.tree.set_model(store)
        self.container.remove(self.container.get_child())
        self.container.add(self.tree)
        self.container.show_all()
        
    def create_model(self, media_path, media_paths_in_db):
        print("start filling mode")

        if media_path is None:
            WarningDialog(
                _("Media path not set"),
                _('Media path not set. You must set the "Base path for relative media paths" in the Preferences.'),
                parent=self.uistate.window
            )
            return

        path_states = self.calculate_path_states(media_path, media_paths_in_db)
        store = self.create_path_state_filesystem_tree_model(media_path, path_states)
        print("stop filling mode")
        return store
    
    def calculate_path_states(self, media_path, media_paths_in_db):
        path_states = {}
        for dir, dirs, files in os.walk(media_path, topdown=False):
            children_count = 0
            children_in_db_count = 0
            children_partially_in_db = 0
            for item in files:
                file_path = os.path.join(dir, item)
                relative_file_path = file_path.replace(media_path + "/", "")
                if relative_file_path in media_paths_in_db:
                    state = PATH_STATE.FULLY_IN_DB
                    children_in_db_count += 1
                else:
                    state = PATH_STATE.NOT_IN_DB
                path_states[file_path] = state
                children_count += 1
                
            
            for subdir in dirs:
                subdir_path = os.path.join(dir, subdir)
                children_count += 1
                if path_states[subdir_path] == PATH_STATE.FULLY_IN_DB:   # raises error when subdir not processed yet. should not happen
                    children_in_db_count += 1
                elif path_states[subdir_path] == PATH_STATE.PARTIALLY_IN_DB:
                    children_partially_in_db += 1
            
            if children_count == 0:
                path_states[dir] = PATH_STATE.IGNORED
            elif children_count == children_in_db_count:
                path_states[dir] = PATH_STATE.FULLY_IN_DB
            elif children_partially_in_db > 0 or children_in_db_count > 0:
                path_states[dir] = PATH_STATE.PARTIALLY_IN_DB
            else:
                path_states[dir] = PATH_STATE.NOT_IN_DB
            
            self.progress_bar.pulse()
            
        return path_states
    
    def create_path_state_filesystem_tree_model(self, media_path, path_states):
        store = Gtk.TreeStore(str, str)
        parents = {}
        for dir, dirs, files in os.walk(media_path, topdown=True):
            
            for subdir in dirs:
                subdir_path = os.path.join(dir, subdir)
                color = COLOR_MAPPING[path_states[subdir_path]]
                parents[subdir_path] = store.append(parents.get(dir, None), [subdir, color])
                
            for item in files:
                file_path = os.path.join(dir, item)
                color = COLOR_MAPPING[path_states[file_path]]
                store.append(parents.get(dir, None), [item, color])
            
            self.progress_bar.pulse()
        return store

    def get_list_of_media_paths_in_db(self):
        media_paths = set()
        for handle in self.dbstate.db.get_media_handles():
            media = self.dbstate.db.get_media_from_handle(handle)
            media_paths.add(media.get_path())
        return media_paths
