import ctypes

from simple_com import COMInterface
from windows.generated_def.winstructs import *

DEBUG_BREAKPOINT_DEFERRED = 0x00000002
DEBUG_BREAKPOINT_ENABLED  = 0x00000004


# https://msdn.microsoft.com/en-us/library/windows/hardware/ff549812%28v=vs.85%29.aspx
class IDebugBreakpoint(COMInterface):
    _functions_ = {
        "QueryInterface": ctypes.WINFUNCTYPE(HRESULT, PVOID, PVOID)(0, "QueryInterface"),
        "AddRef": ctypes.WINFUNCTYPE(HRESULT)(1, "AddRef"),
        "Release": ctypes.WINFUNCTYPE(HRESULT)(2, "Release"),
        # https://msdn.microsoft.com/en-us/library/windows/hardware/ff546827%28v=vs.85%29.aspx
        "GetId": ctypes.WINFUNCTYPE(HRESULT, PULONG)(3, "GetId"),
        # https://msdn.microsoft.com/en-us/library/windows/hardware/ff549370%28v=vs.85%29.aspx
        "GetType": ctypes.WINFUNCTYPE(HRESULT, PULONG)(4, "GetType"),
        # https://msdn.microsoft.com/en-us/library/windows/hardware/ff545576%28v=vs.85%29.aspx
        "GetAdder": ctypes.WINFUNCTYPE(HRESULT, PULONG)(5, "GetAdder"),
        # https://msdn.microsoft.com/en-us/library/windows/hardware/ff546791%28v=vs.85%29.aspx
        "GetFlags": ctypes.WINFUNCTYPE(HRESULT, PULONG)(6, "GetFlags"),
        # https://msdn.microsoft.com/en-us/library/windows/hardware/ff537903%28v=vs.85%29.aspx
        "AddFlags": ctypes.WINFUNCTYPE(HRESULT, ULONG)(7, "AddFlags"),
        # https://msdn.microsoft.com/en-us/library/windows/hardware/ff554504%28v=vs.85%29.aspx
        "RemoveFlags": ctypes.WINFUNCTYPE(HRESULT, ULONG)(8, "RemoveFlags"),
        # https://msdn.microsoft.com/en-us/library/windows/hardware/ff556703%28v=vs.85%29.aspx
        "SetFlags": ctypes.WINFUNCTYPE(HRESULT, ULONG)(9, "SetFlags"),
        # https://msdn.microsoft.com/en-us/library/windows/hardware/ff548008%28v=vs.85%29.aspx
        "GetOffset": ctypes.WINFUNCTYPE(HRESULT, PULONG64)(10, "GetOffset"),
        # https://msdn.microsoft.com/en-us/library/windows/hardware/ff556741%28v=vs.85%29.aspx
        "SetOffset": ctypes.WINFUNCTYPE(HRESULT, ULONG64)(11, "SetOffset"),
        # https://msdn.microsoft.com/en-us/library/windows/hardware/ff546557%28v=vs.85%29.aspx
        "GetDataParameters": ctypes.WINFUNCTYPE(HRESULT, PULONG, PULONG)(12, "GetDataParameters"),
        # https://msdn.microsoft.com/en-us/library/windows/hardware/ff556655%28v=vs.85%29.aspx
        "SetDataParameters": ctypes.WINFUNCTYPE(HRESULT, ULONG, ULONG)(13, "SetDataParameters"),
        # https://msdn.microsoft.com/en-us/library/windows/hardware/ff548104%28v=vs.85%29.aspx
        "GetPassCount": ctypes.WINFUNCTYPE(HRESULT, PULONG)(14, "GetPassCount"),
        # https://msdn.microsoft.com/en-us/library/windows/hardware/ff556759%28v=vs.85%29.aspx
        "SetPassCount": ctypes.WINFUNCTYPE(HRESULT, ULONG)(15, "SetPassCount"),
        # https://msdn.microsoft.com/en-us/library/windows/hardware/ff545769%28v=vs.85%29.aspx
        "GetCurrentPassCount": ctypes.WINFUNCTYPE(HRESULT, PULONG)(16, "GetCurrentPassCount"),
        # https://msdn.microsoft.com/en-us/library/windows/hardware/ff547074%28v=vs.85%29.aspx
        ## NOT SUPPORTED IN KERNEL LAND
        "GetMatchThreadId": ctypes.WINFUNCTYPE(HRESULT, PULONG)(17, "GetMatchThreadId"),
        # https://msdn.microsoft.com/en-us/library/windows/hardware/ff556735%28v=vs.85%29.aspx
        ## NOT SUPPORTED IN KERNEL LAND
        "SetMatchThreadId": ctypes.WINFUNCTYPE(HRESULT, ULONG)(18, "SetMatchThreadId"),
        # https://msdn.microsoft.com/en-us/library/windows/hardware/ff545677%28v=vs.85%29.aspx
        "GetCommand": ctypes.WINFUNCTYPE(HRESULT, PVOID, ULONG, PULONG)(19, "GetCommand"),
        # https://msdn.microsoft.com/en-us/library/windows/hardware/ff556632%28v=vs.85%29.aspx
        "SetCommand": ctypes.WINFUNCTYPE(HRESULT, c_char_p)(20, "SetCommand"),
        # https://msdn.microsoft.com/en-us/library/windows/hardware/ff548048%28v=vs.85%29.aspx
        "GetOffsetExpression": ctypes.WINFUNCTYPE(HRESULT, PVOID, ULONG, PULONG)(21, "GetOffsetExpression"),
        # https://msdn.microsoft.com/en-us/library/windows/hardware/ff556745%28v=vs.85%29.aspx
        "SetOffsetExpression": ctypes.WINFUNCTYPE(HRESULT, c_char_p)(22, "SetOffsetExpression"),
        # https://msdn.microsoft.com/en-us/library/windows/hardware/ff548095%28v=vs.85%29.aspx
        "GetParameters": ctypes.WINFUNCTYPE(HRESULT, PDEBUG_BREAKPOINT_PARAMETERS)(23, "GetParameters"),
    }



class WinBreakpoint(IDebugBreakpoint):
    def __init__(self, comptr, debugger):
        self.dbg = debugger
        super(WinBreakpoint, self).__init__(comptr)

    def enable(self):
        self.AddFlags(DEBUG_BREAKPOINT_ENABLED)

    def disable(self):
        self.RemoveFlags(DEBUG_BREAKPOINT_ENABLED)

    # We don't use SetOffset because if the offset is set using
    # this method, the command set by 'SetCommand' is never executed
    def set_offset(self, addr):
        if isinstance(addr, str):
            return self.set_offset_expression(addr)
        hex_addr = hex(addr).strip("L")
        return self.set_offset_expression(hex_addr)

    def set_offset_expression(self, expr):
        return self.SetOffsetExpression(expr)

    def set_command(self, cmd):
        return self.SetCommand(cmd)

    def get_command(self):
        # Get command len
        cmd_length = ULONG(0)
        self.GetCommand(0, 0, ctypes.byref(cmd_length))
        l = cmd_length.value
        buffer = (ctypes.c_char * l)()
        self.GetCommand(buffer, l, ctypes.byref(cmd_length))
        return buffer[:cmd_length.value - 1]


