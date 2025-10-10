from enum import Enum
import os
import re
from py2docfx.docfx_yaml.logger import get_logger
from py2docfx.convert_prepare.source import Source
from py2docfx.convert_prepare.package_info_extra_settings import extra_exclude_path_by_package

class PackageInfo:
    class InstallType(int, Enum):
        PYPI = 1
        SOURCE_CODE = 2
        DIST_FILE = 3
    path: Source
    def __init__(self) -> None:
        pass

    @classmethod
    def report_error(cls, name, value, condition=None):
        py2docfx_logger = get_logger(__name__)
        if condition:
            message = "When {0}, found unexpected property of {1}, loaded value is: {2}".format(
                condition, name, value
            )
        else:
            message = "Found unexpected property of {0}, loaded value is: {1}".format(
                name, value
            )
        py2docfx_logger.error(message)
        raise ValueError(message)

    @classmethod
    def parse_from(cls, dict, reading_required_packages=False):
        package_info = PackageInfo()
        package_info.exclude_path = dict.get("exclude_path", [])
        package_info.extension_config = dict.get("extension_config", {})
        package_info.sphinx_extensions = dict.get("sphinx_extensions", [])
        if reading_required_packages:
            package_info_dict = dict
        else:
            package_info_dict = dict.get("package_info", None)
            if not package_info_dict:
                cls.report_error("package_info", "None")

        install_type = package_info_dict.get("install_type", None)
        if not install_type or install_type not in {"pypi", "source_code", "dist_file"}:
            cls.report_error("install_type", install_type)
        else:
            package_info.install_type = cls.InstallType[install_type.upper()]

        package_info.name = package_info_dict.get("name", None)
        if not package_info.name and package_info.install_type == cls.InstallType.PYPI:
            cls.report_error("name", "None")

        package_info.version = package_info_dict.get("version", None)
        package_info.extra_index_url = package_info_dict.get("extra_index_url", None)
        package_info.extras = package_info_dict.get("extras", [])

        if package_info.install_type == cls.InstallType.SOURCE_CODE:
            package_info.url = package_info_dict.get("url", None)
            package_info.branch = package_info_dict.get("branch", None)
            package_info.folder = package_info_dict.get("folder", None)

            if not package_info.url:
                py2docfx_logger = get_logger(__name__)
                if not package_info.folder:
                    msg = "When install_type is source_code, url or folder should be provided"
                    py2docfx_logger.error(msg)
                    raise ValueError(msg)
                else:
                    msg = f'Read source code from local folder: {package_info.folder}'
                    py2docfx_logger.info(msg)

        prefer_source_distribution = package_info_dict.get(
            "prefer_source_distribution", False
        )
        package_info.prefer_source_distribution = (
            prefer_source_distribution
            if isinstance(prefer_source_distribution, bool)
            else prefer_source_distribution.lower() == "true"
        )

        if package_info.install_type == cls.InstallType.DIST_FILE:
            package_info.location = package_info_dict.get("location", None)
            if not package_info.location:
                cls.report_error(
                    "location", "None", condition="When install_type is dist_file"
                )

        package_info.build_in_subpackage = package_info_dict.get(
            "build_in_subpackage", False
        )

        package_info.editable = package_info_dict.get("editable", False)
        return package_info

    def get_combined_name_version(self):
        base_name = (
            f"{self.name}[{','.join(extras)}]"
            if (extras := getattr(self, "extras", []))
            else self.name
        )

        version = getattr(self, "version", None)
        if not version:
            return base_name
        elif re.match("^(<|>|<=|>=|==).+$", version.strip()):
            return base_name.strip() + version.strip()
        else:
            return f"{base_name.strip()}=={version.strip()}"

    def get_install_command(self) -> tuple[str, list]:
        if self.install_type == self.InstallType.DIST_FILE:
            if not hasattr(self, "location") or not self.location:
                self.__class__.report_error(
                    "location", "None", condition="When install_type is dist_file"
                )
            return (
                f"{self.location}[{','.join(extras)}]"
                if (extras := getattr(self, "extras", None))
                else self.location,
                [],
            )

        if self.install_type == self.InstallType.PYPI:
            if not hasattr(self, "name") or not self.name:
                self.__class__.report_error(
                    "name", "None", condition="When install_type is pypi"
                )
            pipInstallExtraOptions = []
            if not hasattr(self, "version") or self.version is None:
                pipInstallExtraOptions.append("--upgrade")
            if hasattr(self, "extra_index_url") and self.extra_index_url:
                pipInstallExtraOptions.extend(
                    ["--extra-index-url", self.extra_index_url]
                )
            return (self.get_combined_name_version(), pipInstallExtraOptions)

        if self.install_type == self.InstallType.SOURCE_CODE:
            if not hasattr(self, "path") or not self.path.source_folder:
                self.__class__.report_error(
                    "path.source_folder",
                    "None",
                    condition="When install_type is source_code",
                )
            return (
                f"{self.path.source_folder}[{','.join(extras)}]"
                if (extras := getattr(self, "extras", None))
                else self.path.source_folder,
                [],
            )

        self.__class__.report_error("install_type", self.install_type)


    def get_exluded_command(self) -> list:
        py2docfx_logger = get_logger(__name__)
        if hasattr(self, "path"):
            code_location = self.path.source_folder
        else:
            msg = "Should set source code location before build documents"
            py2docfx_logger.error(msg)
            raise ValueError(msg)
        exclude_path = []
        if code_location:
            exclude_path.append(os.path.join(code_location, "build/*"))
            exclude_path.append(os.path.join(code_location, "setup.py"))
            if hasattr(self, "exclude_path") and self.exclude_path:
                exclude_path.extend(
                    [
                        os.path.join(code_location, path)
                        for path in self.exclude_path
                    ]
                )
            # exclude root package __init__.py, prevent generating azure.yml
            current_parent_packages = ''
            package_name_segs = [seg for seg in self.name.split('-') if seg]
            for idx, package_seg in enumerate(package_name_segs):
                if idx != len(package_name_segs)-1:
                    current_parent_packages = f'{current_parent_packages}/{package_seg}' if current_parent_packages else package_seg
                    exclude_path.append(os.path.join(code_location, f'{current_parent_packages}/__init__.py'))

            if self.name in extra_exclude_path_by_package:
                exclude_path.extend(
                    [
                        os.path.join(code_location, path)
                        for path in extra_exclude_path_by_package[self.name]
                    ]
                )
        return exclude_path
