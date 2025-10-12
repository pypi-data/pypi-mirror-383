from keystone import *
import platform
import struct
import ctypes
import sys

__all__ = ["inline_asm"]

def ks_detect():
    arch = platform.machine().lower()
    endian = "little" if struct.pack("=I", 1)[0] == 1 else "big"

    if arch in ("x86_64", "amd64"):
        return KS_ARCH_X86, KS_MODE_64
    elif arch in ("i386", "i686", "x86"):
        return KS_ARCH_X86, KS_MODE_32
    elif arch.startswith("armv7"):
        return KS_ARCH_ARM, KS_MODE_ARM
    elif arch.startswith("armv6") or arch.startswith("armv5"):
        return KS_ARCH_ARM, KS_MODE_ARM
    elif arch in ("arm64", "aarch64"):
        return KS_ARCH_ARM64, KS_MODE_LITTLE_ENDIAN
    elif arch.startswith("mips"):
        return KS_ARCH_MIPS, KS_MODE_MIPS32
    else:
        raise NotImplementedError(f"Arquitetura não suportada: {arch}")

def run_shellcode_windows(shellcode: bytes):
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

    PAGE_EXECUTE_READWRITE = 0x40
    MEM_COMMIT  = 0x1000
    MEM_RESERVE = 0x2000
    INFINITE    = 0xFFFFFFFF

    VirtualAlloc = kernel32.VirtualAlloc
    VirtualAlloc.restype  = ctypes.c_void_p
    VirtualAlloc.argtypes = [
        ctypes.c_void_p, ctypes.c_size_t,
        ctypes.c_ulong, ctypes.c_ulong
    ]

    CreateThread = kernel32.CreateThread
    CreateThread.restype  = ctypes.c_void_p
    CreateThread.argtypes = [
        ctypes.c_void_p, ctypes.c_size_t,
        ctypes.c_void_p, ctypes.c_void_p,
        ctypes.c_ulong, ctypes.POINTER(ctypes.c_ulong)
    ]

    WaitForSingleObject = kernel32.WaitForSingleObject
    WaitForSingleObject.argtypes = [ctypes.c_void_p, ctypes.c_ulong]

    GetExitCodeThread = kernel32.GetExitCodeThread
    GetExitCodeThread.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ulong)]
    GetExitCodeThread.restype  = ctypes.c_int

    size = len(shellcode)
    addr = VirtualAlloc(
        None, size,
        MEM_COMMIT | MEM_RESERVE,
        PAGE_EXECUTE_READWRITE
    )
    if not addr:
        raise OSError("VirtualAlloc failed")

    ctypes.memmove(addr, shellcode, size)

    thread_id = ctypes.c_ulong()
    hThread = CreateThread(
        None, 0,
        ctypes.c_void_p(addr),
        None, 0,
        ctypes.byref(thread_id)
    )
    if not hThread:
        raise OSError("CreateThread failed")

    WaitForSingleObject(hThread, INFINITE)

    exit_code = ctypes.c_ulong()
    if not GetExitCodeThread(hThread, ctypes.byref(exit_code)):
        raise OSError("GetExitCodeThread failed")

    if exit_code is None:
        return 0

    return int(exit_code.value)

def run_shellcode_linux(shellcode: bytes):
    libc = ctypes.CDLL(None)

    PROT_READ, PROT_WRITE, PROT_EXEC = 1, 2, 4
    MAP_PRIVATE, MAP_ANONYMOUS = 2, 32

    libc.mmap.restype  = ctypes.c_void_p
    libc.mmap.argtypes = [
        ctypes.c_void_p, ctypes.c_size_t,
        ctypes.c_int, ctypes.c_int,
        ctypes.c_int, ctypes.c_long
    ]

    libc.pthread_create.restype  = ctypes.c_int
    libc.pthread_create.argtypes = [
        ctypes.POINTER(ctypes.c_ulong),
        ctypes.c_void_p, ctypes.c_void_p,
        ctypes.c_void_p
    ]

    libc.pthread_join.restype  = ctypes.c_int
    libc.pthread_join.argtypes = [
        ctypes.c_ulong,
        ctypes.POINTER(ctypes.c_void_p)
    ]

    size = len(shellcode)
    addr = libc.mmap(
        None, size,
        PROT_READ | PROT_WRITE | PROT_EXEC,
        MAP_PRIVATE | MAP_ANONYMOUS,
        -1, 0
    )

    if addr in (ctypes.c_void_p(-1).value, None):
        raise OSError("mmap failed")

    ctypes.memmove(addr, shellcode, size)

    thread = ctypes.c_ulong()
    ret = libc.pthread_create(
        ctypes.byref(thread), None,
        ctypes.c_void_p(addr), None
    )
    if ret != 0:
        raise OSError(f"pthread_create failed: {ret}")

    retval = ctypes.c_void_p()
    libc.pthread_join(thread, ctypes.byref(retval))

    if retval.value is None:
        return 0
    
    return int(ctypes.c_long(retval.value).value)

def run_shellcode_macos(shellcode: bytes):
    libSystem = ctypes.CDLL("/usr/lib/libSystem.B.dylib")

    PROT_READ, PROT_WRITE, PROT_EXEC = 1, 2, 4
    MAP_PRIVATE, MAP_ANON = 2, 0x1000

    libSystem.mmap.restype  = ctypes.c_void_p
    libSystem.mmap.argtypes = [
        ctypes.c_void_p, ctypes.c_size_t,
        ctypes.c_int, ctypes.c_int,
        ctypes.c_int, ctypes.c_long
    ]

    libSystem.pthread_create.restype  = ctypes.c_int
    libSystem.pthread_create.argtypes = [
        ctypes.POINTER(ctypes.c_ulong),
        ctypes.c_void_p, ctypes.c_void_p,
        ctypes.c_void_p
    ]

    libSystem.pthread_join.restype  = ctypes.c_int
    libSystem.pthread_join.argtypes = [
        ctypes.c_ulong,
        ctypes.POINTER(ctypes.c_void_p)
    ]

    size = len(shellcode)
    addr = libSystem.mmap(
        None, size,
        PROT_READ | PROT_WRITE | PROT_EXEC,
        MAP_PRIVATE | MAP_ANON,
        -1, 0
    )

    if addr in (ctypes.c_void_p(-1).value, None):
        raise OSError("mmap failed")

    ctypes.memmove(addr, shellcode, size)

    thread = ctypes.c_ulong()
    ret = libSystem.pthread_create(
        ctypes.byref(thread), None,
        ctypes.c_void_p(addr), None
    )
    if ret != 0:
        raise OSError(f"pthread_create failed: {ret}")

    retval = ctypes.c_void_p()
    libSystem.pthread_join(thread, ctypes.byref(retval))

    if retval.value is None:
        return 0
    
    return int(ctypes.c_long(retval.value).value)

def run_shellcode_android_arm64(shellcode: bytes):
    libc = ctypes.CDLL(None)

    PROT_READ, PROT_WRITE, PROT_EXEC = 1, 2, 4
    MAP_PRIVATE, MAP_ANONYMOUS = 2, 0x20

    libc.mmap.restype  = ctypes.c_void_p
    libc.mmap.argtypes = [
        ctypes.c_void_p, ctypes.c_size_t,
        ctypes.c_int, ctypes.c_int,
        ctypes.c_int, ctypes.c_long
    ]

    libc.pthread_create.restype  = ctypes.c_int
    libc.pthread_create.argtypes = [
        ctypes.POINTER(ctypes.c_ulong),
        ctypes.c_void_p, ctypes.c_void_p,
        ctypes.c_void_p
    ]

    libc.pthread_join.restype  = ctypes.c_int
    libc.pthread_join.argtypes = [
        ctypes.c_ulong,
        ctypes.POINTER(ctypes.c_void_p)
    ]

    size = len(shellcode)
    addr = libc.mmap(
        None, size,
        PROT_READ | PROT_WRITE | PROT_EXEC,
        MAP_PRIVATE | MAP_ANONYMOUS,
        -1, 0
    )

    if addr in (ctypes.c_void_p(-1).value, None):
        raise OSError("mmap failed")

    ctypes.memmove(addr, shellcode, size)

    thread = ctypes.c_ulong()
    ret = libc.pthread_create(
        ctypes.byref(thread), None,
        ctypes.c_void_p(addr), None
    )
    if ret != 0:
        raise OSError(f"pthread_create failed: {ret}")

    retval = ctypes.c_void_p()
    libc.pthread_join(thread, ctypes.byref(retval))

    if retval.value is None:
        return 0
    
    return int(ctypes.c_long(retval.value).value)

def inline_asm(code):
    plat = sys.platform

    ks_arch, ks_mode = ks_detect()

    ks = Ks(ks_arch, ks_mode)

    encoding, _ = ks.asm(code)

    shellcode = bytes(encoding)

    if plat.startswith("win"):
        return run_shellcode_windows(shellcode)
    elif plat.startswith("linux") and ks_arch == KS_ARCH_ARM64:
        return run_shellcode_android_arm64(shellcode)
    elif plat.startswith("linux"):
        return run_shellcode_linux(shellcode)
    elif plat == "darwin":
        return run_shellcode_macos(shellcode)
    else:
        raise NotImplementedError(f"Sistema não suportado: {plat}")