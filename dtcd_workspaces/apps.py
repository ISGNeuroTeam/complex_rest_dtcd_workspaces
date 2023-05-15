from django.apps import AppConfig


class DtcdWorkspacesConfig(AppConfig):
    name = 'dtcd_workspaces'
    verbose_name = "Datacad workspaces"

    def ready(self):
        # write here code that is executed when plugin loaded
        self._show_plugin_version()

    @staticmethod
    def _show_plugin_version():
        try:
            from dtcd_workspaces.setup import __version__
            from logging import getLogger
            plugin_log = getLogger('dtcd_workspaces')
            plugin_log.warning(f'dtcd_workspaces plugin version is {__version__}')
        except ImportError:
            log.info(f'No setup.py file with __version__.')
