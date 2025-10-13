# (generated with --quick)

import google
import googledrivefs.googledrivefs
from typing import Any, List, Type

Credentials: Any
GoogleDriveFS: Type[googledrivefs.googledrivefs.GoogleDriveFS]
Opener: Any
__all__: List[str]

class GoogleDriveFSOpener(Any):
    protocols: List[str]
    def open_fs(self, fs_url, parse_result, writeable, create, cwd) -> Any: ...
