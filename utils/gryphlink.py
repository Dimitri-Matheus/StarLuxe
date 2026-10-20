"""Utils for everything related the gryphlink launcher"""

import ctypes
import logging
import os
import threading
from ctypes import wintypes
from pathlib import Path

logger = logging.getLogger(__name__)

CREATE_SUSPENDED = 0x00000004
EXTENDED_STARTUPINFO_PRESENT = 0x00080000
PROC_THREAD_ATTRIBUTE_PARENT_PROCESS = 0x00020000
INFINITE = 0xFFFFFFFF

kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

class STARTUPINFOW(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD), ("lpReserved", wintypes.LPWSTR),
        ("lpDesktop", wintypes.LPWSTR), ("lpTitle", wintypes.LPWSTR),
        ("dwX", wintypes.DWORD), ("dwY", wintypes.DWORD),
        ("dwXSize", wintypes.DWORD), ("dwYSize", wintypes.DWORD),
        ("dwXCountChars", wintypes.DWORD), ("dwYCountChars", wintypes.DWORD),
        ("dwFillAttribute", wintypes.DWORD), ("dwFlags", wintypes.DWORD),
        ("wShowWindow", wintypes.WORD), ("cbReserved2", wintypes.WORD),
        ("lpReserved2", ctypes.POINTER(ctypes.c_byte)),
        ("hStdInput", wintypes.HANDLE), ("hStdOutput", wintypes.HANDLE),
        ("hStdError", wintypes.HANDLE),
    ]

class STARTUPINFOEXW(ctypes.Structure):
    _fields_ = [
        ("StartupInfo", STARTUPINFOW),
        ("lpAttributeList", ctypes.c_void_p),
    ]

class PROCESS_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("hProcess", wintypes.HANDLE), ("hThread", wintypes.HANDLE),
        ("dwProcessId", wintypes.DWORD), ("dwThreadId", wintypes.DWORD),
    ]

kernel32.CreateProcessW.argtypes = (
    wintypes.LPCWSTR, wintypes.LPWSTR, ctypes.c_void_p, ctypes.c_void_p,
    wintypes.BOOL, wintypes.DWORD, ctypes.c_void_p, wintypes.LPCWSTR,
    ctypes.c_void_p, ctypes.c_void_p,
)
kernel32.CreateProcessW.restype = wintypes.BOOL
kernel32.InitializeProcThreadAttributeList.argtypes = (
    ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD, ctypes.POINTER(ctypes.c_size_t),
)
kernel32.InitializeProcThreadAttributeList.restype = wintypes.BOOL
kernel32.UpdateProcThreadAttribute.argtypes = (
    ctypes.c_void_p, wintypes.DWORD, ctypes.c_size_t, ctypes.c_void_p,
    ctypes.c_size_t, ctypes.c_void_p, ctypes.c_void_p,
)
kernel32.UpdateProcThreadAttribute.restype = wintypes.BOOL
kernel32.DeleteProcThreadAttributeList.argtypes = (ctypes.c_void_p,)
kernel32.WaitForSingleObject.argtypes = (wintypes.HANDLE, wintypes.DWORD)
kernel32.WaitForSingleObject.restype = wintypes.DWORD
kernel32.TerminateProcess.argtypes = (wintypes.HANDLE, wintypes.UINT)
kernel32.TerminateProcess.restype = wintypes.BOOL
kernel32.CloseHandle.argtypes = (wintypes.HANDLE,)
kernel32.CloseHandle.restype = wintypes.BOOL

JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000
JobObjectExtendedLimitInformation = 9

class IO_COUNTERS(ctypes.Structure):
    _fields_ = [
        ("ReadOperationCount", ctypes.c_ulonglong),
        ("WriteOperationCount", ctypes.c_ulonglong),
        ("OtherOperationCount", ctypes.c_ulonglong),
        ("ReadTransferCount", ctypes.c_ulonglong),
        ("WriteTransferCount", ctypes.c_ulonglong),
        ("OtherTransferCount", ctypes.c_ulonglong),
    ]

class JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("PerProcessUserTimeLimit", wintypes.LARGE_INTEGER),
        ("PerJobUserTimeLimit", wintypes.LARGE_INTEGER),
        ("LimitFlags", wintypes.DWORD),
        ("MinimumWorkingSetSize", ctypes.c_size_t),
        ("MaximumWorkingSetSize", ctypes.c_size_t),
        ("ActiveProcessLimit", wintypes.DWORD),
        ("Affinity", ctypes.c_size_t),
        ("PriorityClass", wintypes.DWORD),
        ("SchedulingClass", wintypes.DWORD),
    ]

class JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BasicLimitInformation", JOBOBJECT_BASIC_LIMIT_INFORMATION),
        ("IoInfo", IO_COUNTERS),
        ("ProcessMemoryLimit", ctypes.c_size_t),
        ("JobMemoryLimit", ctypes.c_size_t),
        ("PeakProcessMemoryUsed", ctypes.c_size_t),
        ("PeakJobMemoryUsed", ctypes.c_size_t),
    ]

kernel32.CreateJobObjectW.argtypes = (ctypes.c_void_p, wintypes.LPCWSTR)
kernel32.CreateJobObjectW.restype = wintypes.HANDLE
kernel32.SetInformationJobObject.argtypes = (wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD)
kernel32.SetInformationJobObject.restype = wintypes.BOOL
kernel32.AssignProcessToJobObject.argtypes = (wintypes.HANDLE, wintypes.HANDLE)
kernel32.AssignProcessToJobObject.restype = wintypes.BOOL


def find_game_executable(launcher_exe: str) -> Path | None:
    paths = []
    for entry in launcher_exe.parent.iterdir():
        if not entry.is_dir():
            continue
        exe_path = entry / "Games.exe"
        if exe_path.is_file():
            paths.append(exe_path)

    if not paths:
        return None

    def version(path: Path) -> tuple:
        try:
            return tuple(map(int, path.parent.name.split(".")))
        except Exception:
            return (0,)

    return max(paths, key=version)


def start_game_with_launcher(
    games_exe: Path,
    game_exe: Path,
    cwd: Path | None = None,
    args: str = "",
    env_extra: dict[str, str] | None = None,
) -> int:
    launcher = STARTUPINFOW()
    launcher.cb = ctypes.sizeof(STARTUPINFOW)
    process_launcher = PROCESS_INFORMATION()
    cmd_launcher = ctypes.create_unicode_buffer(f'"{games_exe}"')

    if not kernel32.CreateProcessW(
        None, cmd_launcher, None, None, False,
        CREATE_SUSPENDED, None, str(games_exe.parent),
        ctypes.byref(launcher), ctypes.byref(process_launcher),
    ):
        raise ctypes.WinError(ctypes.get_last_error())

    try:
        size = ctypes.c_size_t(0)
        kernel32.InitializeProcThreadAttributeList(None, 1, 0, ctypes.byref(size))
        attribute_list = ctypes.create_string_buffer(size.value)

        if not kernel32.InitializeProcThreadAttributeList(attribute_list, 1, 0, ctypes.byref(size)):
            raise ctypes.WinError(ctypes.get_last_error())

        try:
            parent_handle = ctypes.c_void_p(process_launcher.hProcess)
            if not kernel32.UpdateProcThreadAttribute(
                attribute_list, 0, PROC_THREAD_ATTRIBUTE_PARENT_PROCESS,
                ctypes.byref(parent_handle), ctypes.sizeof(parent_handle),
                None, None,
            ):
                raise ctypes.WinError(ctypes.get_last_error())

            game = STARTUPINFOEXW()
            game.StartupInfo.cb = ctypes.sizeof(STARTUPINFOEXW)
            game.lpAttributeList = ctypes.cast(attribute_list, ctypes.c_void_p)
            process_game = PROCESS_INFORMATION()
            cmd_game = ctypes.create_unicode_buffer(f'"{game_exe}"' + (f" {args}" if args else ""))

            for key, value in (env_extra or {}).items():
                os.environ[key] = value

            try:
                started = kernel32.CreateProcessW(
                    None, cmd_game, None, None, False,
                    EXTENDED_STARTUPINFO_PRESENT, None,
                    str(cwd) if cwd else None,
                    ctypes.byref(game), ctypes.byref(process_game),
                )
            finally:
                for key in (env_extra or {}):
                    os.environ.pop(key, None)

            if not started:
                raise ctypes.WinError(ctypes.get_last_error())

            try:
                job = kernel32.CreateJobObjectW(None, None)
                if not job:
                    raise ctypes.WinError(ctypes.get_last_error())
                
                limit_info = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
                limit_info.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE

                if not kernel32.SetInformationJobObject(
                    job, JobObjectExtendedLimitInformation,
                    ctypes.byref(limit_info), ctypes.sizeof(limit_info),
                ):
                    raise ctypes.WinError(ctypes.get_last_error())

                if not kernel32.AssignProcessToJobObject(job, process_launcher.hProcess):
                    raise ctypes.WinError(ctypes.get_last_error())

            except OSError as e:
                logger.warning(f"Job Object setup failed: {e}")

        finally:
            kernel32.DeleteProcThreadAttributeList(attribute_list)

    except Exception:
        kernel32.TerminateProcess(process_launcher.hProcess, 0)
        kernel32.CloseHandle(process_launcher.hProcess)
        kernel32.CloseHandle(process_launcher.hThread)
        raise

    logger.info(
        f"Started pid {process_game.dwProcessId} "
        f"with parent pid {process_launcher.dwProcessId}, suspended"
    )

    game_process, game_thread = process_game.hProcess, process_game.hThread
    launcher_process, launcher_thread = process_launcher.hProcess, process_launcher.hThread

    def cleanup():
        kernel32.WaitForSingleObject(game_process, INFINITE)
        kernel32.TerminateProcess(launcher_process, 0)
        kernel32.CloseHandle(game_process)
        kernel32.CloseHandle(game_thread)
        kernel32.CloseHandle(launcher_process)
        kernel32.CloseHandle(launcher_thread)
        logger.info("Suspended launcher terminated.")

    threading.Thread(target=cleanup, name="gryphlink-cleanup", daemon=True).start()

    return process_game.dwProcessId