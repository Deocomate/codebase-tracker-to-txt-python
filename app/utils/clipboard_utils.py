"""Windows clipboard file-copy utilities."""

import ctypes
import platform
import struct

WINDOWS_COPY_SUPPORT = False
if platform.system() == "Windows":
    try:
        import win32clipboard
        import win32con

        WINDOWS_COPY_SUPPORT = True
    except ImportError:
        WINDOWS_COPY_SUPPORT = False


def is_clipboard_copy_supported() -> bool:
    """Check if file-copy-to-clipboard is supported on this platform."""
    return WINDOWS_COPY_SUPPORT


def copy_files_to_clipboard(file_paths: list[str]) -> None:
    """
    Copy a list of file paths to the Windows clipboard as CF_HDROP.
    Raises NotImplementedError on unsupported platforms.
    """
    if not WINDOWS_COPY_SUPPORT:
        raise NotImplementedError(
            "File clipboard copy requires Windows with pywin32."
        )

    dropfiles_header = struct.pack("IiiII", 20, 0, 0, 0, 1)
    files_blob = ("\0".join(file_paths) + "\0\0").encode("utf-16le")
    data = dropfiles_header + files_blob

    kernel32 = ctypes.windll.kernel32
    kernel32.GlobalAlloc.restype = ctypes.c_void_p
    kernel32.GlobalLock.restype = ctypes.c_void_p
    kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
    kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
    kernel32.GlobalFree.argtypes = [ctypes.c_void_p]

    gmem_moveable = 0x0002
    hglobal = kernel32.GlobalAlloc(gmem_moveable, len(data))
    if not hglobal:
        raise RuntimeError("GlobalAlloc failed.")

    locked = kernel32.GlobalLock(hglobal)
    if not locked:
        kernel32.GlobalFree(hglobal)
        raise RuntimeError("GlobalLock failed.")

    try:
        ctypes.memmove(locked, data, len(data))
    finally:
        kernel32.GlobalUnlock(hglobal)

    opened = False
    try:
        win32clipboard.OpenClipboard()
        opened = True
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32con.CF_HDROP, hglobal)
    except Exception:
        kernel32.GlobalFree(hglobal)
        raise
    finally:
        if opened:
            try:
                win32clipboard.CloseClipboard()
            except Exception:
                pass
