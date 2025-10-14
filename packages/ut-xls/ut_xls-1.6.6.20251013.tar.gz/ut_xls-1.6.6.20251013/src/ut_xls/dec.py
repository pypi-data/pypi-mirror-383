from ut_path.pathk import PathK

from typing import Any
TyDic = dict[Any, Any]
TyPath = str
TyPathK = str


def sh_static_path(func):
    def wrapper(*args):
        pathk = args[0]
        kwargs = args[1]
        print("========================================")
        print(f"pathk = {pathk}")
        print(f"kwargs = {kwargs}")
        print("========================================")
        _path: TyPath = PathK.sh_path(pathk, kwargs)
        return func(_path, kwargs, *args[2:])
    return wrapper


def sh_class_path(func):
    def wrapper(*args):
        cls = args[0]
        pathk = args[1]
        kwargs = args[2]
        print("========================================")
        print(f"pathk = {pathk}")
        print(f"kwargs = {kwargs}")
        print("========================================")
        _path: TyPath = PathK.sh_path(pathk, kwargs)
        return func(cls, _path, kwargs, *args[3:])
    return wrapper
