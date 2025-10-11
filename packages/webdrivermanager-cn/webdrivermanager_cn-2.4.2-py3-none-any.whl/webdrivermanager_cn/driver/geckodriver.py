from webdrivermanager_cn.core.driver import DriverManager, DriverType
from webdrivermanager_cn.core.mirror_manager import MirrorType
from webdrivermanager_cn.core.os_manager import OSType
from webdrivermanager_cn.core.version_manager import VersionManager, GeckodriverVersionManager


class Geckodriver(DriverManager):
    def __init__(self, version='latest', path=None, mirror_type: MirrorType = None):
        super().__init__(
            driver_name=DriverType.firefox,
            version=version,
            root_dir=path,
            mirror_type=mirror_type
        )

    @property
    def version_manager(self) -> VersionManager:
        return GeckodriverVersionManager(self.driver_version)

    @property
    def download_url(self) -> str:
        mirror = self.mirror.mirror_url()
        return f'{mirror}/{self.download_version}/{self.get_driver_name}'

    @property
    def get_driver_name(self) -> str:
        pack_type = 'zip' if self.os_manager.is_win else 'tar.gz'
        return f'{self.driver_name}-{self.download_version}-{self.os_info}.{pack_type}'

    @property
    def os_info(self):
        os_type_suffix = self.os_manager.get_os_architecture
        os_type = self.os_manager.get_os_name
        if self.os_manager.is_aarch64:
            os_type_suffix = '-aarch64'
        elif os_type == OSType.MAC:
            os_type_suffix = ''
            os_type = 'macos'
        return f'{os_type}{os_type_suffix}'
