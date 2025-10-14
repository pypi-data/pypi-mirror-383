from ut_path.pathk import PathK

from typing import Any
TyDic = dict[Any, Any]
TyPath = str
TyPathK = str


def sh_static_path(func):
    def wrapper(pathk: TyPathK, kwargs: TyDic, *args):
        print("========================================")
        print(f"pathk = {pathk}")
        print(f"kwargs = {kwargs}")
        print(f"args = {args}")
        print("========================================")
        _path: TyPath = PathK.sh_path(pathk, kwargs)
        return func(_path, kwargs, *args)
    return wrapper


def sh_class_path(func):
    def wrapper(cls, pathk: TyPathK, kwargs: TyDic, *args):
        print("========================================")
        print(f"pathk = {pathk}")
        print(f"kwargs = {kwargs}")
        print(f"args = {args}")
        print("========================================")
        _path: TyPath = PathK.sh_path(pathk, kwargs)
        return func(_path, kwargs, *args)
    return wrapper
