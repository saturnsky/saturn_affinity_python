# This code is based on https://stackoverflow.com/questions/66027768/how-to-invoke-getlogicalprocessorinformation-in-python.
# Author: https://stackoverflow.com/users/235698/mark-tolonen


from ctypes import *
from ctypes import wintypes as w

ULONG_PTR = c_size_t  # c_ulong on Win32, c_ulonglong on Win64.
ULONGLONG = c_ulonglong

ERROR_INSUFFICIENT_BUFFER = 122


class CACHE_DESCRIPTOR(Structure):
    _fields_ = (
        ("Level", w.BYTE),
        ("Associativity", w.BYTE),
        ("LineSize", w.WORD),
        ("Size", w.DWORD),
        ("Type", c_int),
    )


class ProcessorCore(Structure):
    _fields_ = (("Flags", w.BYTE),)


class NumaNode(Structure):
    _fields_ = (("NodeNumber", w.DWORD),)


class DUMMYUNIONNAME(Union):
    _fields_ = (
        ("ProcessorCore", ProcessorCore),
        ("NumaNode", NumaNode),
        ("Cache", CACHE_DESCRIPTOR),
        ("Reserved", ULONGLONG * 2),
    )


class SYSTEM_LOGICAL_PROCESSOR_INFORMATION(Structure):
    _anonymous_ = ("DUMMYUNIONNAME",)
    _fields_ = (
        ("ProcessorMask", ULONG_PTR),
        ("Relationship", c_int),
        ("DUMMYUNIONNAME", DUMMYUNIONNAME),
    )


dll = WinDLL("kernel32", use_last_error=True)
dll.GetLogicalProcessorInformation.argtypes = (
    POINTER(SYSTEM_LOGICAL_PROCESSOR_INFORMATION),
    w.LPDWORD,
)
dll.GetLogicalProcessorInformation.restype = w.BOOL


# wrapper for easier use
def GetLogicalProcessorInformation():
    bytelength = w.DWORD()
    structlength = sizeof(SYSTEM_LOGICAL_PROCESSOR_INFORMATION)
    # Call with null buffer to get required buffer size
    result = dll.GetLogicalProcessorInformation(None, byref(bytelength))
    if (err := get_last_error()) != ERROR_INSUFFICIENT_BUFFER:
        raise WinError(err)
    no_of_structures = bytelength.value // structlength
    arr = (SYSTEM_LOGICAL_PROCESSOR_INFORMATION * no_of_structures)()
    result = dll.GetLogicalProcessorInformation(arr, byref(bytelength))
    if not result:
        raise WinError(get_last_error())
    return arr
