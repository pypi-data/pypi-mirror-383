from webdrivermanager_cn.core.driver import DriverManager, DriverType
from webdrivermanager_cn.core.mirror_manager import MirrorType
from webdrivermanager_cn.core.version_manager import ChromeDriverVersionManager


class ChromeDriver(DriverManager):
    def __init__(self, version='latest', path=None, mirror_type: MirrorType = None):
        super().__init__(
            driver_name=DriverType.chrome,
            version=version,
            root_dir=path,
            mirror_type=mirror_type,
        )

    @property
    def download_url(self) -> str:
        new_version = self.version_manager.is_new_version
        mirror = self.mirror.mirror_url(new_version)
        if self.mirror.is_huawei or (self.mirror.is_ali and not new_version):
            url = f'{mirror}/{self.download_version}/{self.get_driver_name}'
        else:
            url = f'{mirror}/{self.download_version}/{self.os_info}/{self.get_driver_name}'
        self.log.debug(f'拼接下载url {self.mirror_type} - {url}')
        return url

    @property
    def version_manager(self):
        return ChromeDriverVersionManager(version=self.driver_version)

    @property
    def get_driver_name(self) -> str:
        name = f"chromedriver-{self.os_info}.zip"
        return name if self.version_manager.is_new_version else name.replace('-', '_')

    @property
    def os_info(self):
        os_type = f"{self.os_manager.get_os_type}{self.os_manager.get_framework}"
        is_new_version = self.version_manager.is_new_version
        if self.os_manager.is_mac:
            mac_suffix = self.os_manager.get_mac_framework
            if mac_suffix and mac_suffix in os_type:
                return "mac-arm64" if is_new_version else 'mac64_m1'
            return "mac-x64" if is_new_version else 'mac64'
        elif self.os_manager.is_win:
            if not self.version_manager.is_new_version:
                return 'win32'
        return os_type
