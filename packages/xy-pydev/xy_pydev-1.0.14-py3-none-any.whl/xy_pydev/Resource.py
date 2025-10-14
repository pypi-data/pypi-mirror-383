# -*- coding: UTF-8 -*-
__author__ = "余洋"
__doc__ = "Resource"
"""
  * @File    :   Resource.py
  * @Time    :   2023/06/03 10:54:41
  * @Author  :   余洋
  * @Version :   1.0
  * @Contact :   yuyangit.0515@qq.com
  * @License :   (C)Copyright 2019-2024, Ship of Ocean
  * @Desc    :   None
"""

import shutil
import subprocess
from .ModuleData import ModuleData
from pathlib import Path
from xy_console.utils import printt, inputt, _error, _run, _success, _seperate_text

# `Traversable` was moved in newer Python versions to importlib.resources.abc
# Try importing the modern location first, fall back to the older location.
# We expose `Traversable` for use in annotations, and keep `_TraversableType`
# as the concrete runtime class (or None) for safe isinstance checks.
try:
    from importlib.resources.abc import Traversable as _TraversableType
except Exception:
    try:
        from importlib.abc import Traversable as _TraversableType
    except Exception:
        _TraversableType = None


class Resource:
    _module_data: ModuleData = ModuleData()

    def __init__(self) -> None:
        self.ci_yml = self.read_text(self._module_data.ci_yml)
        self.gitignore = self.read_text(self._module_data.gitignore)
        self.manifest = self.read_text(self._module_data.manifest)
        self.pyproject = self.read_text(self._module_data.pyproject)
        self.setup = self.read_text(self._module_data.setup)
        self.version = self.read_text(self._module_data.version)
        self.main = self.read_text(self._module_data.main)
        self.module = self.read_text(self._module_data.module)
        self.module_data = self.read_text(self._module_data.module_data)
        self.base_module_data = self.read_text(self._module_data.base_module_data)
        self.resource = self.read_text(self._module_data.resource)
        python_path = f"{Path(subprocess.getoutput('which python')).parent}/"
        vscode_settings_content = self.read_text(self._module_data.vscode_settings)
        self.vscode_settings = (
            vscode_settings_content.format(python_path=python_path)
            if isinstance(vscode_settings_content, str)
            else None
        )

    def read_text(self, file_path: Path | Traversable | None) -> str | None:
        if (
            isinstance(file_path, Path) and file_path.exists() and file_path.is_file()
        ) or (isinstance(file_path, Traversable) and file_path.is_file()):
            return file_path.read_text()
        return None

    def read_bytes(self, file_path: Path | Traversable | None) -> bytes | None:
        if (
            isinstance(file_path, Path) and file_path.exists() and file_path.is_file()
        ) or (isinstance(file_path, Traversable) and file_path.is_file()):
            return file_path.read_bytes()
        return None

    def project_scripts(
        self,
        module_name: str,
        comment: str = "#",
    ):
        return f'{comment}[project.scripts]\n{comment}{module_name} = "{module_name}.execute.Main:main"'

    def manifest_content(
        self,
        module_name: str,
    ) -> str | None:
        return (
            self.manifest.format(
                module_name=module_name,
            )
            if isinstance(self.manifest, str)
            else None
        )

    def pyproject_content(self, module_name: str, scripts: bool = False) -> str | None:
        project_scripts = (
            self.project_scripts(
                module_name,
                comment="",
            )
            if scripts is True
            else self.project_scripts(
                module_name,
            )
        )
        return (
            self.pyproject.format(
                module_name=module_name,
                project_scripts=project_scripts,
            )
            if isinstance(self.pyproject, str)
            else None
        )

    def main_content(
        self,
        module_name: str,
        module_class_name: str | None,
    ) -> str | None:
        return (
            self.main.format(
                module_name=module_name,
                module_class=module_class_name,
            )
            if isinstance(self.main, str)
            else None
        )

    def module_content(
        self,
        module_class_name: str | None,
    ):
        return (
            self.module.format(
                module_class_name=module_class_name,
            )
            if isinstance(self.module, str)
            else None
        )

    def module_data_content(self, module_name: str) -> str | None:
        return (
            self.module_data.format(
                module_name=module_name,
            )
            if isinstance(self.module_data, str)
            else None
        )

    def base_module_data_content(self, module_name: str) -> str | None:
        return (
            self.base_module_data.format(
                module_name=module_name,
            )
            if isinstance(self.base_module_data, str)
            else None
        )

    def write(
        self,
        module_name: str,
        module_class_name: str,
        scripts: bool = False,
    ):

        self._module_data.write(
            self._module_data.ci_yml_path(),
            self.ci_yml,
        )
        self._module_data.write(
            self._module_data.gitignore_path(),
            self.gitignore,
        )
        self._module_data.write(
            self._module_data.manifest_path(),
            self.manifest_content(module_name),
        )
        self._module_data.write(
            self._module_data.pyproject_path(),
            self.pyproject_content(
                module_name,
                scripts=scripts,
            ),
        )
        self._module_data.write(
            self._module_data.setup_path(),
            self.setup,
        )
        self._module_data.write(
            self._module_data.version_path(),
            self.version,
        )
        self._module_data.write(
            self._module_data.vscode_settings_path(),
            self.vscode_settings,
        )
        self._module_data.write(
            self._module_data.execute_init_path(
                module_name=module_name,
            ),
            "",
        )
        self._module_data.write(
            self._module_data.main_path(
                module_name=module_name,
            ),
            self.main_content(
                module_name=module_name,
                module_class_name=module_class_name,
            ),
        )
        self._module_data.write(
            self._module_data.module_path_init_path(
                module_name=module_name,
            ),
            "",
        )
        self._module_data.write(
            self._module_data.module_path(
                module_name=module_name,
                module_class_name=module_class_name,
            ),
            self.module_content(
                module_class_name=module_class_name,
            ),
        )
        self._module_data.write(
            self._module_data.module_data_path(
                module_name=module_name,
            ),
            self.module_data_content(
                module_name=module_name,
            ),
        )
        self._module_data.write(
            self._module_data.base_module_data_path(
                module_name=module_name,
            ),
            self.base_module_data_content(
                module_name=module_name,
            ),
        )
        self._module_data.write(
            self._module_data.resource_path(
                module_name=module_name,
            ),
            self.resource,
        )

    clean_target_name_list = [
        "dist",
        ".egg-info",
        "build",
    ]

    def clean_tagged(self, name: str) -> bool:
        for target_name in self.clean_target_name_list:
            if target_name in name:
                return True
        return False

    def clean(self):
        printt(
            f"{_seperate_text}即将清理包含以下列表中名称的目录或者文件: \n{self.clean_target_name_list}",
            style=_run,
        )
        cwd_children = self._module_data.root_path.glob("./*/")
        clean_target_path_list = []
        for child in cwd_children:
            if child.is_dir() is True and self.clean_tagged(child.name) is True:
                clean_target_path_list.append(child)
        if not clean_target_path_list or len(clean_target_path_list) == 0:
            printt(
                f"{_seperate_text}当前目录下无缓存",
                style=_run,
            )
        else:
            printt(
                f"{_seperate_text}检测到以下缓存",
                style=_run,
            )
            for target_path in clean_target_path_list:
                printt(
                    f"{target_path.name}",
                    style=_run,
                )
            validate = inputt(
                f"{_seperate_text}是否确定删除缓存?\nY ==> [确定]\n其他 ==> [取消]\n请输入[Y/n]\n"
            )
            if validate == "Y":
                for target_path in clean_target_path_list:
                    if target_path.is_dir() is True:
                        try:
                            shutil.rmtree(target_path)
                        except Exception:
                            printt(
                                f"{_seperate_text}删除路径失败 : {target_path}",
                                style=_error,
                            )
                    else:
                        try:
                            target_path.unlink()
                        except Exception:
                            printt(
                                f"{_seperate_text}删除文件失败 : {target_path}",
                                style=_error,
                            )
                printt(
                    f"{_seperate_text}删除完成!!!",
                    style=_success,
                )
            else:
                printt(
                    f"{_seperate_text}取消删除缓存",
                    style=_success,
                )
