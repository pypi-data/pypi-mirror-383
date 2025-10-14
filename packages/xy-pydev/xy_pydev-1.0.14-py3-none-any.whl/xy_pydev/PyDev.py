# -*- coding: UTF-8 -*-
__author__ = "余洋"
__doc__ = "PyDev"
"""
  * @File    :   PyDev.py
  * @Time    :   2023/06/03 10:29:52
  * @Author  :   余洋
  * @Version :   1.0
  * @Contact :   yuyangit.0515@qq.com
  * @License :   (C)Copyright 2019-2024, Ship of Ocean
  * @Desc    :   None
"""
import os
from argparse import Namespace
from pathlib import Path
from xy_file.Object.File import File
from xy_argparse.ArgParse import ArgParse
from xy_console.utils import inputt, printt, print_s, print_e, print_r
from xy_string.utils import is_empty_string, contains_zh
import xy_pydev
from .ModuleData import ModuleData
from .Resource import Resource


class PyDev(ArgParse):
    _module_data = ModuleData()
    _resource = Resource()

    def __init__(self) -> None:
        self.quick_default_info(xy_pydev.__name__)
        self.description = "python模块开发工具"

    def main(self):
        self.default_parser()
        self.add_arguments()
        self.parse_arguments()
        if self.work():
            self.run_arguments()

    def add_arguments(self):
        self.add_argument(
            flag="-w",
            name="--work",
            help_text="""
                工作方式:
                1.clean | c => 清理模块缓存,
                2.build | b => 编译, python -m build,
                3.sdist | sd => python setup.py sdist bdist_wheel,
                4.utpi | ut => 提交到test.pypi.org, upload to test.pypi.org,
                5.upi | u => 提交到pypi.org, upload to pypi.org,
                6.其他  => 创建项目,
            """,
            default="create",
        )
        self.add_argument(
            flag="-n",
            name="--name",
            help_text="""
                Python模块名称 不能包含中文
            """,
            default="",
        )
        self.add_argument(
            flag="-m",
            name="--module_class_name",
            type_name=str,
            help_text="""
                模块入口类名称 不能包含中文
            """,
            default="",
        )
        self.add_argument(
            flag="-s",
            name="--scripts",
            type_name=bool,
            help_text="""
                是否开启全局命令
            """,
            default=False,
        )

    def work(self):
        arguments = self.arguments()
        if isinstance(arguments, Namespace):
            return arguments.work
        return None

    def module_class_name(self):
        arguments = self.arguments()
        if isinstance(arguments, Namespace):
            return arguments.module_class_name
        return None

    def scripts(self):
        arguments = self.arguments()
        if isinstance(arguments, Namespace):
            return arguments.scripts
        return None

    def module_name(self):
        arguments = self.arguments()
        if isinstance(arguments, Namespace):
            return arguments.name
        return None

    def input_module_class_name(self, default: str) -> str | None:
        validate = inputt(
            f"是否需要修改模块入口类名称?\n当前为: {default}\n不能包含中文\nY=>代表[需要];\n其他=>代表[不需要]\n请输入[ Y/n ]\n",
        )
        if validate == "Y":
            module_class_name = inputt(
                f"请输入新的模块入口类名称\n当前为: {default}\n不能包含中文\n",
            )
            if is_empty_string(module_class_name) or contains_zh(module_class_name):
                return self.input_module_class_name(default)
            else:
                return module_class_name
        return default

    def run(self, module_name: str | None):
        printt(f"新模块名称为: {module_name}")
        module_class_name = self.module_class_name()
        if not is_empty_string(module_name) and is_empty_string(module_class_name):
            module_class_name = self.input_module_class_name("Runner")
        scripts = self.scripts()
        if scripts is False:
            scripts_input = inputt(
                f"是否需要添加全局命令?\nY=>代表[添加];\n其他=>代表[不添加]\n请输入[ Y/n ]\n",
            )
            if scripts_input == "Y":
                scripts = True
            else:
                scripts = False
        self._module_data.root_path = Path.cwd().joinpath(module_name)
        self._module_data.make_dirs(
            module_name=module_name,
        )
        self._resource._module_data.root_path = Path.cwd().joinpath(module_name)
        self._resource.write(
            module_name=str(module_name),
            module_class_name=str(module_class_name),
            scripts=scripts if scripts else False,
        )
        print_s(
            f"新模块[{module_name}]创建完成!!!",
        )

    def input_module_name(self) -> str | None:
        module_name = inputt(
            f"请输入新模块名称, 不能包含中文\n",
        )
        if is_empty_string(module_name) or contains_zh(module_name):
            return self.input_module_name()

        return module_name

    def create_dir_check(self, module_name) -> bool:
        module_path = Path.cwd().joinpath(module_name)
        if module_path.exists():
            print_e(f"路径 {module_path} 已存在, 请确认后再进行模块创建")
            return False
        else:
            if os.access(Path.cwd(), os.R_OK) and os.access(Path.cwd(), os.W_OK):
                return True
            else:
                print_e(
                    f"路径[{module_path}]不合法或者没有权限, 请确认后再进行模块创建"
                )
        return False

    def create_dir(self, module_name):
        module_path = Path.cwd().joinpath(module_name)
        if os.access(Path.cwd(), os.R_OK) and os.access(Path.cwd(), os.W_OK):
            return File.touch(module_path)
        return None

    def create(self):
        module_name = self.module_name()
        if is_empty_string(module_name):
            module_name = self.input_module_name()
            if is_empty_string(module_name):
                print_e(f"请输入新模块名称，不能包含中文")
            else:
                if contains_zh(module_name):
                    printt(f"新模块名称[{module_name}]不能包含中文")
                else:
                    validate = self.create_dir_check(module_name)
                    if validate:
                        self.run(module_name)
        else:
            if contains_zh(module_name):
                printt(f"新模块名称[{module_name}]不能包含中文")
            else:
                validate = self.create_dir_check(module_name)
                if validate:
                    self.run(module_name=str(module_name))

    def clean(self):
        print_r(
            "开始清理模块缓存...",
        )
        self._resource.clean()

    def build(self):
        os.system("python -m build")

    def sdist(self):
        os.system("python setup.py sdist bdist_wheel")

    def utpi(self):
        os.system("python -m twine upload --repository testpypi dist/* --verbose")

    def upi(self):
        os.system("python -m twine upload dist/* --verbose")

    def on_arguments(
        self,
        name,
        value,
        arguments=None,
    ):
        if name == "work":
            if value == "clean" or value == "c":
                self.clean()
                return False
            elif value == "build" or value == "b":
                self.build()
                return False
            elif value == "sdist" or value == "sd":
                self.sdist()
                return False
            elif value == "utpi" or value == "ut":
                self.utpi()
                return False
            elif value == "upi" or value == "u":
                self.upi()
                return False
        self.create()
        return False
