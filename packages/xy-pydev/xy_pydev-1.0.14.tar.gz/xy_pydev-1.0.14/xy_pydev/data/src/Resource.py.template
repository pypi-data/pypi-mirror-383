# -*- coding: UTF-8 -*-
__author__ = '余洋'
__doc__ = 'Resource'
'''
  * @File    :   Resource.py
  * @Time    :   2023/06/03 10:54:41
  * @Author  :   余洋
  * @Version :   1.0
  * @Contact :   yuyangit.0515@qq.com
  * @License :   (C)Copyright 2019-2024, Ship of Ocean
  * @Desc    :   None
'''

from importlib.abc import Traversable
from pathlib import Path
from .ModuleData import ModuleData


class Resource():
    _module_data: ModuleData = ModuleData()

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