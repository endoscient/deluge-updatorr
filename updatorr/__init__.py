from deluge.plugins.init import PluginInitBase


VERSION = (0, 1, 5)


class CorePlugin(PluginInitBase):

    def __init__(self, plugin_name):
        from core import Core as _plugin_cls
        self._plugin_cls = _plugin_cls
        super(CorePlugin, self).__init__(plugin_name)


class GtkUIPlugin(PluginInitBase):

    def __init__(self, plugin_name):
        from gtkui import GtkUI as _plugin_cls
        self._plugin_cls = _plugin_cls
        super(GtkUIPlugin, self).__init__(plugin_name)
