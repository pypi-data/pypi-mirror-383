# -*- coding: UTF-8 -*-
__author__ = "余洋"
__doc__ = "ModuleData"
"""
  * @File    :   ModuleData.py
  * @Time    :   2023/06/03 10:36:13
  * @Author  :   余洋
  * @Version :   1.0
  * @Contact :   yuyangit.0515@qq.com
  * @License :   (C)Copyright 2019-2024, Ship of Ocean
  * @Desc    :   None
"""
from importlib_resources import files
import xy_pydev
from .BaseModuleData import BaseModuleData


class ModuleData(BaseModuleData):
    ci_yml_name = ".xy-codehub-ci.yml"
    gitignore_name = ".gitignore"
    manifest_name = "MANIFEST.in"
    pyproject_name = "pyproject.toml"
    setup_name = "setup.py"
    version_name = "VERSION"
    main_name = "execute/Main.py"
    module_name = "src/Module.py"
    module_data_name = "src/ModuleData.py"
    base_module_data_name = "src/BaseModuleData.py"
    resource_name = "src/Resource.py"
    utils_name = "src/utils.py"
    vscode_settings_name = ".vscode/settings.json"

    def __init__(self):
        self.data_path = files(xy_pydev.__name__).joinpath("data")  # type: ignore
        self.ci_yml = self.make_data_template(
            self.ci_yml_name,
        )
        self.gitignore = self.make_data_template(
            self.gitignore_name,
        )
        self.manifest = self.make_data_template(
            self.manifest_name,
        )
        self.pyproject = self.make_data_template(
            self.pyproject_name,
        )
        self.setup = self.make_data_template(
            self.setup_name,
        )
        self.version = self.make_data_template(
            self.version_name,
        )
        self.main = self.make_data_template(
            self.main_name,
        )
        self.module = self.make_data_template(
            self.module_name,
        )
        self.module_data = self.make_data_template(
            self.module_data_name,
        )
        self.base_module_data = self.make_data_template(
            self.base_module_data_name,
        )
        self.resource = self.make_data_template(
            self.resource_name,
        )
        self.vscode_settings = self.make_data_template(
            self.vscode_settings_name,
        )

    def ci_yml_path(self):
        return self.root_path.joinpath(self.ci_yml_name)

    def gitignore_path(self):
        return self.root_path.joinpath(self.gitignore_name)

    def manifest_path(self):
        return self.root_path.joinpath(self.manifest_name)

    def pyproject_path(self):
        return self.root_path.joinpath(self.pyproject_name)

    def setup_path(self):
        return self.root_path.joinpath(self.setup_name)

    def version_path(self):
        return self.root_path.joinpath(self.version_name)

    def execute_path(self, module_name: str):
        return self.make_src_path(module_name, "execute")

    def vscode_settings_path(self):
        return self.root_path.joinpath(self.vscode_settings_name)

    def main_path(
        self,
        module_name: str,
    ):
        return self.make_src_path(
            module_name=module_name,
            file_name=self.main_name,
        )

    def execute_init_path(
        self,
        module_name: str,
    ):
        return self.make_src_path(
            module_name=module_name,
            file_name="execute/__init__.py",
        )

    def module_path_init_path(
        self,
        module_name: str,
    ):
        return self.make_src_path(
            module_name=module_name,
            file_name="__init__.py",
        )

    def module_path(
        self,
        module_name: str,
        module_class_name: str,
    ):
        return self.make_src_path(
            module_name=module_name,
            file_name=f"{module_class_name}.py",
        )

    def module_data_path(self, module_name: str):
        return self.make_src_path(
            module_name=module_name,
            file_name="ModuleData.py",
        )

    def base_module_data_path(self, module_name: str):
        return self.make_src_path(
            module_name=module_name,
            file_name="BaseModuleData.py",
        )

    def resource_path(self, module_name: str):
        return self.make_src_path(
            module_name=module_name,
            file_name="Resource.py",
        )

    def utils_path(self, module_name: str):
        return self.make_src_path(
            module_name=module_name,
            file_name="utils.py",
        )

    def make_dirs(self, module_name: str | None):
        data_path = self.make_src_path(
            module_name=module_name,
            file_name="data",
        )
        (
            data_path.mkdir(
                parents=True,
                exist_ok=True,
            )
            if data_path
            else ""
        )
        test_path = self.root_path.joinpath("test")
        test_path.mkdir(
            parents=True,
            exist_ok=True,
        )
        test_init_path = test_path.joinpath("__init__.py")
        test_init_path.touch()

        samples_path = self.root_path.joinpath("samples")
        samples_path.mkdir(
            parents=True,
            exist_ok=True,
        )
