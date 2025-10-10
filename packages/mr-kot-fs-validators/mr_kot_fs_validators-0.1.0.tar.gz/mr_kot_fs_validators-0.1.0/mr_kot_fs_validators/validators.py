"""
Validators for filesystem state, permissions and mounts.
"""

from __future__ import annotations

import os
import stat as statmod
from functools import wraps
from pathlib import Path
from typing import Callable, Iterable, Optional, Union

from mr_kot.status import Status as StatusEnum
from mr_kot.validators import Validator, ValidatorResult

# Some minimal environments (non-Unix, busybox, containers, or frozen builds) may
# lack the standard Unix account/group databases, or importing pwd/grp may fail.
# We attempt to import them and fall back to None so ownership/group validators
# can degrade gracefully (return ERROR for unknown user/group resolution) instead
# of crashing on import
try:
    import grp  # type: ignore
    import pwd  # type: ignore
except Exception:  # pragma: no cover - very rare environments
    pwd = None  # type: ignore
    grp = None  # type: ignore


# ----------------------------
# helpers
# ----------------------------

def _result(status: Union[str, StatusEnum], evidence: str) -> ValidatorResult:
    se = StatusEnum[status.upper()] if isinstance(status, str) else status
    return (se, evidence)


def _format_mode(mode: int) -> str:
    return f"{mode & 0o777:04o}"


def _to_path(p: Union[str, Path]) -> Path:
    return p if isinstance(p, Path) else Path(p)


def _try_stat(path: Union[str, Path], follow_symlinks: bool = False) -> Optional[os.stat_result]:
    p = _to_path(path)
    try:
        # Python 3.9: os.stat supports follow_symlinks
        return os.stat(str(p), follow_symlinks=follow_symlinks)
    except FileNotFoundError:
        return None


def _resolve_user_uid(user: Union[str, int]) -> Optional[int]:
    if isinstance(user, int):
        return user
    if isinstance(user, str):
        if pwd is None:
            return None
        try:
            return pwd.getpwnam(user).pw_uid
        except KeyError:
            return None
    return None


def _resolve_group_gid(group: Union[str, int]) -> Optional[int]:
    if isinstance(group, int):
        return group
    if isinstance(group, str):
        if grp is None:
            return None
        try:
            return grp.getgrnam(group).gr_gid
        except KeyError:
            return None
    return None


def _iter_recursive(root: Union[str, Path], follow_symlinks: bool) -> Iterable[Path]:
    r = _to_path(root)
    for dirpath, dirnames, filenames in os.walk(str(r), followlinks=follow_symlinks):
        dpath = Path(dirpath)
        yield dpath
        for name in dirnames:
            yield dpath / name
        for name in filenames:
            yield dpath / name


def _exc_to_error(func: Callable[[Union[str, Path]], ValidatorResult]) -> Callable[[Union[str, Path]], ValidatorResult]:
    """Decorator-like wrapper that converts unexpected exceptions into ERROR.

    Keeps existing specific exception handling intact; only triggers on uncaught exceptions.
    Evidence format: "path=<target> error=<ExcType>: <message>".
    """
    @wraps(func)
    def _wrapper(target: Union[str, Path]) -> ValidatorResult:
        try:
            return func(target)
        except Exception as e:
            return _result("ERROR", f"path={target} error={type(e).__name__}: {e}")

    return _wrapper


# ----------------------------
# Existence and type
# ----------------------------

def Exists() -> Validator:
    """Pass if path exists."""

    def _v(path: Union[str, Path]) -> ValidatorResult:
        p = _to_path(path)
        if p.exists():
            return _result("PASS", f"path={p} exists")
        return _result("FAIL", f"path={p} missing")

    return _exc_to_error(_v)


def IsFile() -> Validator:
    """Pass if path is a regular file (follows symlinks)."""

    def _v(path: Union[str, Path]) -> ValidatorResult:
        p = _to_path(path)
        if p.is_file():
            return _result("PASS", f"path={p} is_file")
        if not p.exists():
            return _result("FAIL", f"path={p} missing")
        return _result("FAIL", f"path={p} not_file")

    return _exc_to_error(_v)


def IsDir() -> Validator:
    """Pass if path is a directory (follows symlinks)."""

    def _v(path: Union[str, Path]) -> ValidatorResult:
        p = _to_path(path)
        if p.is_dir():
            return _result("PASS", f"path={p} is_dir")
        if not p.exists():
            return _result("FAIL", f"path={p} missing")
        return _result("FAIL", f"path={p} not_dir")

    return _exc_to_error(_v)

def IsSymlink() -> Validator:
    """Pass if path is a symbolic link (lstat)."""

    def _v(path: Union[str, Path]) -> ValidatorResult:
        p = _to_path(path)
        if p.is_symlink():
            return _result("PASS", f"path={p} is_symlink")
        if not p.exists():
            return _result("FAIL", f"path={p} missing")
        return _result("FAIL", f"path={p} not_symlink")

    return _exc_to_error(_v)


def _is_socket(mode: int) -> bool:
    return statmod.S_ISSOCK(mode)

def _is_block(mode: int) -> bool:
    return statmod.S_ISBLK(mode)

def _is_char(mode: int) -> bool:
    return statmod.S_ISCHR(mode)


def IsSocket() -> Validator:
    """Pass if path is a UNIX domain socket."""

    def _v(path: Union[str, Path]) -> ValidatorResult:
        st = _try_stat(path, follow_symlinks=False)
        if st is None:
            return _result("FAIL", f"path={path} missing")
        if _is_socket(st.st_mode):
            return _result("PASS", f"path={path} is_socket")
        return _result("FAIL", f"path={path} not_socket")

    return _exc_to_error(_v)


def IsBlockDevice() -> Validator:
    """Pass if path is a block device node."""

    def _v(path: Union[str, Path]) -> ValidatorResult:
        st = _try_stat(path, follow_symlinks=False)
        if st is None:
            return _result("FAIL", f"path={path} missing")
        if _is_block(st.st_mode):
            return _result("PASS", f"path={path} is_block_device")
        return _result("FAIL", f"path={path} not_block_device")

    return _exc_to_error(_v)


def IsCharDevice() -> Validator:
    """Pass if path is a character device node."""

    def _v(path: Union[str, Path]) -> ValidatorResult:
        st = _try_stat(path, follow_symlinks=False)
        if st is None:
            return _result("FAIL", f"path={path} missing")
        if _is_char(st.st_mode):
            return _result("PASS", f"path={path} is_char_device")
        return _result("FAIL", f"path={path} not_char_device")

    return _exc_to_error(_v)


# ----------------------------
# Permissions and ownership
# ----------------------------

def HasMode(expected_octal: Union[str, int], recursive: bool = False, follow_symlinks: bool = False) -> Validator:
    """Pass if file mode matches expected octal string or int (0775 etc).

    Parameters:
    - expected_octal: str or int representing permission bits (e.g., "0755" or 0o755)
    - recursive: if target is a dir, traverse and fail on first mismatch
    - follow_symlinks: use stat() instead of lstat()

    Evidence examples:
    PASS: path=/data mode expected=0755 actual=0755
    FAIL: path=/data child=/data/x.txt mode expected=0644 actual=0600
    """

    if isinstance(expected_octal, str):
        try:
            exp = int(expected_octal, 8)
        except ValueError as e:
            raise ValueError("expected_octal must be octal string like '0755'") from e
    elif isinstance(expected_octal, int):
        exp = expected_octal
    else:
        raise ValueError("expected_octal must be str or int")

    def _check_one(p: Path, root: Path) -> Optional[ValidatorResult]:
        st = _try_stat(p, follow_symlinks=follow_symlinks)
        if st is None:
            return _result("FAIL", f"path={p} missing")
        actual = st.st_mode & 0o777
        if actual != (exp & 0o777):
            return _result(
                "FAIL",
                f"path={root} child={p} mode expected={_format_mode(exp)} actual={_format_mode(actual)}",
            )
        return None

    def _v(path: Union[str, Path]) -> ValidatorResult:
        p = _to_path(path)
        st = _try_stat(p, follow_symlinks=follow_symlinks)
        if st is None:
            return _result("FAIL", f"path={p} missing")
        if recursive and p.is_dir():
            for cp in _iter_recursive(p, follow_symlinks):
                res = _check_one(cp, p)
                if res is not None:
                    return res
            return _result("PASS", f"path={p} mode expected={_format_mode(exp)}")
        # non-recursive
        actual = st.st_mode & 0o777
        if actual == (exp & 0o777):
            return _result("PASS", f"path={p} mode expected={_format_mode(exp)}")
        return _result("FAIL", f"path={p} mode expected={_format_mode(exp)} actual={_format_mode(actual)}")

    return _exc_to_error(_v)


def OwnerIs(user: Union[str, int], recursive: bool = False, follow_symlinks: bool = False) -> Validator:
    """Pass if uid owner equals given user (name or uid). Recursive for dirs.

    Evidence examples:
    PASS: path=/data owner expected=mysql actual=mysql
    FAIL: path=/data child=/data/logs/old owner expected=mysql actual=root
    """

    uid = _resolve_user_uid(user)

    def _owner_name(u: int) -> str:
        if pwd is not None:
            try:
                return pwd.getpwuid(u).pw_name
            except KeyError:
                pass
        return str(u)

    def _v(path: Union[str, Path]) -> ValidatorResult:
        if uid is None:
            return _result("ERROR", f"path={path} error=UnknownUser: {user}")
        root = _to_path(path)
        paths: Iterable[Path] = (
            _iter_recursive(root, follow_symlinks) if (recursive and root.is_dir()) else [root]
        )
        for cp in paths:
            st = _try_stat(cp, follow_symlinks=follow_symlinks)
            if st is None:
                return _result("FAIL", f"path={root} child={cp} missing")
            if st.st_uid != uid:
                return _result(
                    "FAIL",
                    f"path={root} child={cp} owner expected={_owner_name(uid)} actual={_owner_name(st.st_uid)}",
                )
        return _result("PASS", f"path={root} owner expected={_owner_name(uid)}")

    return _exc_to_error(_v)


def GroupIs(group: Union[str, int], recursive: bool = False, follow_symlinks: bool = False) -> Validator:
    """Pass if gid group equals given group (name or gid). Recursive for dirs."""

    gid = _resolve_group_gid(group)

    def _group_name(g: int) -> str:
        if grp is not None:
            try:
                return grp.getgrgid(g).gr_name
            except KeyError:
                pass
        return str(g)

    def _v(path: Union[str, Path]) -> ValidatorResult:
        if gid is None:
            return _result("ERROR", f"path={path} error=UnknownGroup: {group}")
        root = _to_path(path)
        paths: Iterable[Path] = (
            _iter_recursive(root, follow_symlinks) if (recursive and root.is_dir()) else [root]
        )
        for cp in paths:
            st = _try_stat(cp, follow_symlinks=follow_symlinks)
            if st is None:
                return _result("FAIL", f"path={root} child={cp} missing")
            if st.st_gid != gid:
                return _result(
                    "FAIL",
                    f"path={root} child={cp} group expected={_group_name(gid)} actual={_group_name(st.st_gid)}",
                )
        return _result("PASS", f"path={root} group expected={_group_name(gid)}")

    return _exc_to_error(_v)


def IsExecutable(by_user: bool = True, by_group: bool = False, by_others: bool = False) -> Validator:
    """Pass if the selected exec bits are set (defaults: user only)."""

    def _v(path: Union[str, Path]) -> ValidatorResult:
        st = _try_stat(path, follow_symlinks=True)
        if st is None:
            return _result("FAIL", f"path={path} missing")
        mask = 0
        if by_user:
            mask |= statmod.S_IXUSR
        if by_group:
            mask |= statmod.S_IXGRP
        if by_others:
            mask |= statmod.S_IXOTH
        if mask == 0:
            mask = statmod.S_IXUSR | statmod.S_IXGRP | statmod.S_IXOTH
        ok = bool(st.st_mode & mask)
        return _result("PASS" if ok else "FAIL", f"path={path} exec={'set' if ok else 'unset'}")

    return _exc_to_error(_v)


def IsReadable(by_user: bool = True, by_group: bool = False, by_others: bool = False) -> Validator:
    """Pass if the selected read bits are set (defaults: user only)."""

    def _v(path: Union[str, Path]) -> ValidatorResult:
        st = _try_stat(path, follow_symlinks=True)
        if st is None:
            return _result("FAIL", f"path={path} missing")
        mask = 0
        if by_user:
            mask |= statmod.S_IRUSR
        if by_group:
            mask |= statmod.S_IRGRP
        if by_others:
            mask |= statmod.S_IROTH
        if mask == 0:
            mask = statmod.S_IRUSR | statmod.S_IRGRP | statmod.S_IROTH
        ok = bool(st.st_mode & mask)
        return _result("PASS" if ok else "FAIL", f"path={path} read={'set' if ok else 'unset'}")

    return _exc_to_error(_v)


def IsWritable(by_user: bool = True, by_group: bool = False, by_others: bool = False) -> Validator:
    """Pass if the selected write bits are set (defaults: user only)."""

    def _v(path: Union[str, Path]) -> ValidatorResult:
        st = _try_stat(path, follow_symlinks=True)
        if st is None:
            return _result("FAIL", f"path={path} missing")
        mask = 0
        if by_user:
            mask |= statmod.S_IWUSR
        if by_group:
            mask |= statmod.S_IWGRP
        if by_others:
            mask |= statmod.S_IWOTH
        if mask == 0:
            mask = statmod.S_IWUSR | statmod.S_IWGRP | statmod.S_IWOTH
        ok = bool(st.st_mode & mask)
        return _result("PASS" if ok else "FAIL", f"path={path} write={'set' if ok else 'unset'}")

    return _exc_to_error(_v)


# ----------------------------
# Content and size
# ----------------------------



def Empty() -> Validator:
    """Pass if file size is 0 or directory has no entries."""

    def _v(path: Union[str, Path]) -> ValidatorResult:
        p = _to_path(path)
        if not p.exists():
            return _result("FAIL", f"path={p} missing")
        if p.is_dir():
            try:
                entries = list(p.iterdir())
            except Exception as e:
                return _result("ERROR", f"path={p} error={type(e).__name__}: {e}")
            ok = len(entries) == 0
            return _result("PASS" if ok else "FAIL", f"path={p} dir_empty={'yes' if ok else 'no'}")
        st = os.stat(str(p), follow_symlinks=True)
        ok = st.st_size == 0
        return _result("PASS" if ok else "FAIL", f"path={p} size={st.st_size} expected=0")

    return _exc_to_error(_v)


def SizeBetween(min_bytes: Optional[int] = None, max_bytes: Optional[int] = None) -> Validator:
    """Pass if file size is within [min_bytes, max_bytes]. Bounds can be None."""

    def _v(path: Union[str, Path]) -> ValidatorResult:
        st = _try_stat(path, follow_symlinks=True)
        if st is None:
            return _result("FAIL", f"path={path} missing")
        size = st.st_size
        if min_bytes is not None and size < min_bytes:
            return _result("FAIL", f"path={path} size expected>={min_bytes} actual={size}")
        if max_bytes is not None and size > max_bytes:
            return _result("FAIL", f"path={path} size expected<={max_bytes} actual={size}")
        return _result("PASS", f"path={path} size={size} within_bounds")

    return _exc_to_error(_v)


# ----------------------------
# State, links, and consistency
# ----------------------------

def SymlinkPointsTo(expected_path: str) -> Validator:
    """Pass if symlink target equals expected_path (not resolved)."""

    def _v(path: Union[str, Path]) -> ValidatorResult:
        p = _to_path(path)
        if not p.is_symlink():
            if not p.exists():
                return _result("FAIL", f"path={p} missing")
            return _result("FAIL", f"path={p} not_symlink")
        actual = os.readlink(str(p))
        if actual == expected_path:
            return _result("PASS", f"path={p} link target expected={expected_path}")
        return _result("FAIL", f"path={p} link target expected={expected_path} actual={actual}")

    return _exc_to_error(_v)


def RecentThan(path_or_timestamp: Union[str, Path, int, float]) -> Validator:
    """Pass if target mtime is newer than path_or_timestamp (path or epoch seconds)."""

    def _v(path: Union[str, Path]) -> ValidatorResult:
        st = _try_stat(path, follow_symlinks=True)
        if st is None:
            return _result("FAIL", f"path={path} missing")
        target_mtime = st.st_mtime
        if isinstance(path_or_timestamp, (int, float)):
            ref_mtime = float(path_or_timestamp)
            ref_desc = str(ref_mtime)
        elif isinstance(path_or_timestamp, (str, Path)):
            st2 = _try_stat(path_or_timestamp, follow_symlinks=True)
            if st2 is None:
                return _result("FAIL", f"path={path} ref_missing={path_or_timestamp}")
            ref_mtime = st2.st_mtime
            ref_desc = path_or_timestamp
        else:
            return _result("ERROR", f"path={path} error=InvalidReference")
        ok = target_mtime > ref_mtime
        return _result(
            "PASS" if ok else "FAIL",
            f"path={path} newer_than={ref_desc} is={'yes' if ok else 'no'}",
        )

    return _exc_to_error(_v)




def HasSubdirs(expected_names: list[str], allow_extra: bool = False) -> Validator:
    """Pass if target directory has the expected subdirectory names.
    If allow_extra=False, extras will cause FAIL; otherwise only ensure all expected exist.
    """

    expected = set(expected_names)

    def _v(path: Union[str, Path]) -> ValidatorResult:
        p = _to_path(path)
        if not p.exists():
            return _result("FAIL", f"path={p} missing")
        if not p.is_dir():
            return _result("FAIL", f"path={p} not_dir")
        names = {n.name for n in p.iterdir() if n.is_dir()}
        missing = expected - names
        extras = names - expected
        if missing:
            return _result("FAIL", f"path={p} subdirs missing={sorted(missing)}")
        if not allow_extra and extras:
            return _result("FAIL", f"path={p} subdirs unexpected={sorted(extras)}")
        return _result("PASS", f"path={p} subdirs ok")

    return _exc_to_error(_v)


def HasFiles(expected_names: list[str], allow_extra: bool = False) -> Validator:
    """Pass if target directory has the expected file names (non-directories)."""

    expected = set(expected_names)

    def _v(path: Union[str, Path]) -> ValidatorResult:
        p = _to_path(path)
        if not p.exists():
            return _result("FAIL", f"path={p} missing")
        if not p.is_dir():
            return _result("FAIL", f"path={p} not_dir")
        names = {n.name for n in p.iterdir() if n.is_file()}
        missing = expected - names
        extras = names - expected
        if missing:
            return _result("FAIL", f"path={p} files missing={sorted(missing)}")
        if not allow_extra and extras:
            return _result("FAIL", f"path={p} files unexpected={sorted(extras)}")
        return _result("PASS", f"path={p} files ok")

    return _exc_to_error(_v)


# ----------------------------
# Mounts, devices, capacity
# ----------------------------

def _parse_mountinfo() -> list[dict]:
    entries: list[dict] = []
    try:
        with open("/proc/self/mountinfo", encoding="utf-8", errors="replace") as f:
            for line in f:
                # https://www.kernel.org/doc/Documentation/filesystems/proc.txt
                # fields before '-' are variable; after '-' are: fstype, source, super-options
                parts = line.strip().split(" - ")
                left = parts[0].split()
                right = parts[1].split() if len(parts) > 1 else []
                # mount point is field 5 on the left (0-based index 4)
                mp = left[4] if len(left) > 5 else None
                fstype = right[0] if right else None
                if mp:
                    entries.append({"mount_point": mp, "fstype": fstype, "raw": line.strip()})
    except Exception as e:
        raise RuntimeError(f"mountinfo_parse_failed: {e}") from e
    return entries


def _find_mount_for_path(path: Union[str, Path]) -> Optional[dict]:
    try:
        p = os.path.realpath(str(_to_path(path)))
        entries = _parse_mountinfo()
        best = None
        best_len = -1
        for e in entries:
            mp = e["mount_point"]
            # ensure trailing separator match semantics
            if (p == mp or p.startswith(mp.rstrip("/") + "/")) and len(mp) > best_len:
                best = e
                best_len = len(mp)
        return best
    except Exception as e:
        raise RuntimeError(str(e)) from e


def FSTypeIs(expected_type: str) -> Validator:
    """Pass if filesystem type of mount containing path equals expected_type (e.g., ext4, xfs, nfs)."""

    def _v(path: Union[str, Path]) -> ValidatorResult:
        try:
            entry = _find_mount_for_path(path)
            if entry is None:
                return _result("ERROR", f"path={path} error=MountNotFound")
            actual = entry.get("fstype")
            if actual == expected_type:
                return _result("PASS", f"path={path} fstype expected={expected_type}")
            return _result("FAIL", f"path={path} fstype expected={expected_type} actual={actual}")
        except RuntimeError as e:
            return _result("ERROR", f"path={path} error={e}")
        except Exception as e:
            return _result("ERROR", f"path={path} error={type(e).__name__}: {e}")

    return _exc_to_error(_v)


def MountExists(mount_point: str) -> Validator:
    """Pass if mount point is present in /proc/self/mountinfo."""

    def _v(_: Union[str, Path]) -> ValidatorResult:
        try:
            entries = _parse_mountinfo()
            exists = any(e["mount_point"] == mount_point for e in entries)
            return _result("PASS" if exists else "FAIL", f"mount={mount_point} exists={'yes' if exists else 'no'}")
        except RuntimeError as e:
            return _result("ERROR", f"mount={mount_point} error={e}")
        except Exception as e:
            return _result("ERROR", f"mount={mount_point} error={type(e).__name__}: {e}")

    return _exc_to_error(_v)


def FreeSpaceAtLeast(bytes_min: int) -> Validator:
    """Pass if free space on the filesystem of path is at least bytes_min (statvfs)."""

    def _v(path: Union[str, Path]) -> ValidatorResult:
        p = _to_path(path)
        st = os.statvfs(str(p))
        free = st.f_bavail * st.f_frsize
        ok = free >= bytes_min
        return _result("PASS" if ok else "FAIL", f"path={p} free_bytes={free} threshold={bytes_min}")

    return _exc_to_error(_v)


def DeviceAvailable(device_path: Union[str, Path]) -> Validator:
    """Pass if device node exists and is accessible (char or block)."""

    def _v(_: Union[str, Path]) -> ValidatorResult:
        try:
            dp = _to_path(device_path)
            if not os.path.exists(str(dp)):
                return _result("FAIL", f"path={dp} missing")
            st = os.lstat(str(dp))
            ok = statmod.S_ISCHR(st.st_mode) or statmod.S_ISBLK(st.st_mode)
            return _result("PASS" if ok else "FAIL", f"path={dp} device_node={'yes' if ok else 'no'}")
        except Exception as e:
            return _result("ERROR", f"path={device_path} error={type(e).__name__}: {e}")

    return _exc_to_error(_v)


# ----------------------------
# I/O smoke tests
# ----------------------------
def CanReadFile() -> Validator:
    """Pass if opening file in rb and reading at least 1 byte succeeds."""

    def _v(path: Union[str, Path]) -> ValidatorResult:
        try:
            p = _to_path(path)
            with p.open("rb") as f:
                b = f.read(1)
            ok = len(b) > 0
            return _result("PASS" if ok else "FAIL", f"path={p} read bytes={len(b)}")
        except FileNotFoundError:
            return _result("FAIL", f"path={path} missing")
        # Capability failure -> FAIL (not ERROR) for smoke test
        except (PermissionError, IsADirectoryError) as e:
            return _result("FAIL", f"path={path} error={type(e).__name__}: {e}")

    return _exc_to_error(_v)


def CanWriteFile() -> Validator:
    """Pass if we can create/write/remove a small file inside target directory.
    Evidence includes the final file path on FAIL/ERROR when applicable."""

    def _v(path: Union[str, Path]) -> ValidatorResult:
        test_path = None
        try:
            p = _to_path(path)
            if not p.exists():
                return _result("FAIL", f"path={p} missing")
            if not p.is_dir():
                return _result("FAIL", f"path={p} not_dir")
            name = ".mr_kot_fs_probe.tmp"
            test_path = p / name
            with test_path.open("wb") as f:
                f.write(b"x")
            try:
                test_path.unlink()
            except Exception as e:
                return _result("ERROR", f"path={p} tmp={test_path} error={type(e).__name__}: {e}")
            return _result("PASS", f"path={p} wrote tmp={test_path}")
        except FileNotFoundError:
            return _result("FAIL", f"path={path} missing")
        except (PermissionError, IsADirectoryError) as e:
            return _result("FAIL", f"path={path} tmp={test_path} error={type(e).__name__}: {e}")
        except Exception as e:
            return _result("ERROR", f"path={path} tmp={test_path} error={type(e).__name__}: {e}")

    return _exc_to_error(_v)
