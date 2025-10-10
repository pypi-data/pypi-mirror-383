"""
mr_kot_fs_validators

Reusable filesystem validator factories for Mr. Kot checks. These validators are
small factories returning callables of the form `validator(target_path) -> (status, evidence)`.

Compose them inside your project checks using `check_all()` from Mr. Kot, e.g.:

    from mr_kot import check, check_all
    from mr_kot_fs_validators.validators import Exists, IsFile, HasMode

    @check("/etc/hosts")
    def hosts_file(target):
        return check_all(target,
                         Exists(),
                         IsFile(),
                         HasMode("0644"))
"""

from .validators import (
    CanReadFile,
    CanWriteFile,
    DeviceAvailable,
    Empty,
    Exists,
    FreeSpaceAtLeast,
    FSTypeIs,
    GroupIs,
    HasFiles,
    HasMode,
    HasSubdirs,
    IsBlockDevice,
    IsCharDevice,
    IsDir,
    IsExecutable,
    IsFile,
    IsReadable,
    IsSocket,
    IsSymlink,
    IsWritable,
    MountExists,
    OwnerIs,
    RecentThan,
    SizeBetween,
    SymlinkPointsTo,
)

__all__ = [
    "CanReadFile",
    "CanWriteFile",
    "DeviceAvailable",
    "Empty",
    "Exists",
    "FSTypeIs",
    "FreeSpaceAtLeast",
    "GroupIs",
    "HasFiles",
    "HasMode",
    "HasSubdirs",
    "IsBlockDevice",
    "IsCharDevice",
    "IsDir",
    "IsExecutable",
    "IsFile",
    "IsReadable",
    "IsSocket",
    "IsSymlink",
    "IsWritable",
    "MountExists",
    "OwnerIs",
    "RecentThan",
    "SizeBetween",
    "SymlinkPointsTo",
]
