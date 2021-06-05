from requests import exceptions as requests_exceptions

from briefcase.exceptions import MissingToolError, NetworkFailure


class LinuxDeploy:
    name = 'linuxdeploy'
    full_name = 'linuxdeploy'

    def __init__(self, command):
        self.command = command

    @property
    def appimage_name(self):
        return 'linuxdeploy-{command.host_arch}.AppImage'.format(command=self.command)

    @property
    def linuxdeploy_download_url(self):
        return (
            'https://github.com/linuxdeploy/linuxdeploy/'
            'releases/download/continuous/{self.appimage_name}'.format(self=self)
        )

    @property
    def linuxdeploy_plugin_download_urls(self):
        return [
            'https://raw.githubusercontent.com/linuxdeploy/linuxdeploy-plugin-gtk/master/linuxdeploy-plugin-gtk.sh',
            'https://raw.githubusercontent.com/layday/instawow/feat-webview-gui/gui-webview/linuxdeploy-plugin-instawow-webkit2gtk.sh',
        ]

    @property
    def appimage_path(self):
        return self.command.tools_path / self.appimage_name

    @classmethod
    def verify(cls, command, install=True):
        """
        Verify that LinuxDeploy is available.

        :param command: The command that needs to use linuxdeploy
        :param install: Should the tool be installed if it is not found?
        :returns: A valid LinuxDeploy SDK wrapper. If linuxdeploy is not
            available, and was not installed, raises MissingToolError.
        """
        linuxdeploy = LinuxDeploy(command)

        if not linuxdeploy.exists():
            if install:
                linuxdeploy.install()
            else:
                raise MissingToolError('linuxdeploy')

        return LinuxDeploy(command)

    def exists(self):
        return self.appimage_path.exists()

    @property
    def managed_install(self):
        return True

    def install(self):
        """
        Download and install linuxdeploy.
        """
        try:
            for url in [self.linuxdeploy_download_url, *self.linuxdeploy_plugin_download_urls]:
                path = self.command.download_url(
                    url=url,
                    download_path=self.command.tools_path,
                )
                self.command.os.chmod(str(path), 0o755)
        except requests_exceptions.ConnectionError:
            raise NetworkFailure('downloading linuxdeploy AppImage and plugins')

    def upgrade(self):
        """
        Upgrade an existing linuxdeploy install.
        """
        if self.exists():
            print("Removing old LinuxDeploy install...")
            self.appimage_path.unlink()

            self.install()
            print("...done.")
        else:
            raise MissingToolError('linuxdeploy')
