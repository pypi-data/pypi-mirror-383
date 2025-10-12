from typing import Any, TypeAlias

import openpyxl as op

from ut_path.pathk import PathK
from ut_xls.op.pathioowb import PathIooWb

TyWb: TypeAlias = op.workbook.workbook.Workbook

TyArr = list[Any]
TyDic = dict[Any, Any]
TyAoA = list[TyArr]
TyAoD = list[TyDic]
TyDoAoA = dict[Any, TyAoA]
TyDoAoD = dict[Any, TyAoD]
TyPath = str
TyPathK = str
TySheet = int | str

TnPath = None | TyPath
TnWb = None | TyWb


def sh_path(func):
    def wrapper(pathk: TyPathK, kwargs: TyDic, *args):
        _path: TyPath = PathK.sh_path(pathk, kwargs)
        return func(_path, kwargs, *args)
    return wrapper


class PathKIooWb:

    @staticmethod
    @sh_path
    def write(pathk: TyPathK, kwargs: TyDic, wb: TnWb) -> None:
        PathIooWb.write(pathk, wb)

    @staticmethod
    @sh_path
    def write_wb_from_doaod(pathk: TyPathK, kwargs: TyDic, doaod: TyDoAoD) -> None:
        if not doaod:
            return
        PathIooWb.write_wb_from_doaod(pathk, doaod)
