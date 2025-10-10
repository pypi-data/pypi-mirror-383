# mr-kot-fs-validators

Reusable filesystem validator factories for Mr. Kot checks.
This package provides a set of validator factories that you compose inside your own checks using `check_all()`.

## Usage

```python
from mr_kot import check, check_all
from mr_kot_fs_validators import (
    Exists, IsFile, HasMode, OwnerIs, GroupIs
)

@check
def hosts_file_state():
    return check_all(
        "/etc/hosts",
        Exists(),
        IsFile(),
        HasMode("0644"),
        OwnerIs("root"),
        GroupIs("root"),
    )
```

Each validator is a small factory returning a callable: `validator(target_path) -> (status, evidence)`.
Statuses follow Mr. Kot conventions: `PASS`, `FAIL`, `ERROR` (and occasionally `WARN`).

## Evidence style

- PASS: `path=/etc/hosts exists`
- FAIL: `path=/data mode expected=0755 actual=0775`
- FAIL(recursive): `path=/data child=/data/logs/old owner expected=mysql actual=root`
- ERROR: `path=/var/log error=PermissionError: [Errno 13] Permission denied`

## Validators

- **Existence and type**: `Exists`, `IsFile`, `IsDir`, `IsSymlink`, `IsSocket`, `IsBlockDevice`, `IsCharDevice`.
- **Permissions/ownership**: `HasMode`, `OwnerIs`, `GroupIs`, `IsExecutable`, `IsReadable`, `IsWritable`.
- **Content/size**: `Empty`, `SizeBetween`.
- **State/links**: `SymlinkPointsTo`, `RecentThan`, `HasSubdirs`, `HasFiles`.
- Mounts/devices/capacity: `FSTypeIs`, `MountExists`, `FreeSpaceAtLeast`, `DeviceAvailable`.
- I/O smoke: `CanReadFile`, `CanWriteFile`.

## Notes

- `recursive=True` in `HasMode`, `OwnerIs`, `GroupIs` traverses directories with `os.walk` and fails on the first mismatch.
- `follow_symlinks` controls stat-like checks; default `False` unless stated otherwise.
- `RecentThan()` accepts a file path or an epoch timestamp (float or int).
- `FSTypeIs`/`MountExists` parse `/proc/self/mountinfo` on Linux.
- I/O smoke tests avoid leaving artifacts; `CanWriteFile()` always removes the temporary file it creates.

### Permissions shortcuts

`IsExecutable(by_user=True, by_group=False, by_others=False)`, `IsReadable(...)`, and `IsWritable(...)` accept flags to select which bits to require. If all flags are `False`, they fall back to checking any of the three categories.
