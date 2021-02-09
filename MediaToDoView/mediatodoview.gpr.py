# Copied from QuiltView in order to add make icon work
if locals().get('uistate'):
    from gi.repository import Gtk, GdkPixbuf
    import os
    from gramps.gen.const import USER_PLUGINS
    fname = os.path.join(USER_PLUGINS, 'MediaToDoView')
    icons = Gtk.IconTheme().get_default()
    icons.append_search_path(fname)

register(VIEW,
         id="media-todo-view",
         name=_("Media Todo View"),
         description=_("a program that says 'Hello World'"),
         status=STABLE,
         version="0.0.1",
         gramps_target_version = '5.1',
         #fname="mediatodoview.py",
         fname="mediatodoview.py",
         category = ("Media", _("Media")),
         viewclass = 'MediaToDoView',
         stock_icon = 'media-todo-icon'
         )
