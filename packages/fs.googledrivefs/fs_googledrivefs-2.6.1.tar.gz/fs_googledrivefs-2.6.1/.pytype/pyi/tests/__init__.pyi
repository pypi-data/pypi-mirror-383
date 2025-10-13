# (generated with --quick)

import __future__
import fs
import os
from typing import List, TypeVar, Union, overload

absolute_import: __future__._Feature
newPath: List[str]
unicode_literals: __future__._Feature

AnyStr = TypeVar('AnyStr', str, bytes)

@overload
def join(a: Union[bytes, os.PathLike[bytes]], *paths: Union[bytes, os.PathLike[bytes]]) -> bytes: ...
@overload
def join(a: Union[str, os.PathLike[str]], *paths: Union[str, os.PathLike[str]]) -> str: ...
def realpath(filename: Union[os.PathLike[AnyStr], AnyStr]) -> AnyStr: ...
