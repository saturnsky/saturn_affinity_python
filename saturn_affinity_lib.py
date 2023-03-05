# -*- coding: utf-8 -*-

import win32process
import win32api
import win32con
import win32gui

processed_process = None
processed_time = 0
game_only_mode = False
game_set = set()


def get_number_of_processors():
    sysinfo = win32api.GetSystemInfo()
    return sysinfo[5]


def get_pname_from_window_hwnd(hwnd):
    try:
        pid = win32process.GetWindowThreadProcessId(hwnd)
        handle = win32api.OpenProcess(win32con.MAXIMUM_ALLOWED, win32con.FALSE, pid[1])
        p_name = win32process.GetModuleFileNameEx(handle, 0)
        win32api.CloseHandle(handle)
        return pid, p_name
    except Exception as e:
        return None


def get_current_process():
    for retry in range(0, 3):
        try:
            hwnd = win32gui.GetForegroundWindow()
            process = get_pname_from_window_hwnd(hwnd)
            text = win32gui.GetWindowText(hwnd)
            return process[0], process[1], text
        except Exception as e:
            return None


def get_all_windows():
    def callback(hwnd, hwnds):
        if win32gui.IsWindowVisible(hwnd):
            try:
                process = get_pname_from_window_hwnd(hwnd)
                text = win32gui.GetWindowText(hwnd)
                if text:
                    hwnds.append((process[0], process[1], win32gui.GetWindowText(hwnd)))
            except Exception as e:
                pass
        return True

    hwnds = []
    win32gui.EnumWindows(callback, hwnds)
    return hwnds


def set_affinity_all_process(target_pname=None):
    enum_processes = win32process.EnumProcesses()
    for pid in enum_processes:
        try:
            handle = win32api.OpenProcess(win32con.MAXIMUM_ALLOWED, win32con.FALSE, pid)
            p_name = win32process.GetModuleFileNameEx(handle, 0)
            if handle:
                if target_pname is not None:
                    if p_name == target_pname[1]:
                        if win32process.GetProcessAffinityMask(handle)[0] != half_processors_mask:
                            win32process.SetProcessAffinityMask(handle, half_processors_mask)
                    else:
                        if win32process.GetProcessAffinityMask(handle)[0] != otherwise_processors_mask:
                            win32process.SetProcessAffinityMask(handle, otherwise_processors_mask)
                else:
                    if win32process.GetProcessAffinityMask(handle)[0] != all_processors_mask:
                        win32process.SetProcessAffinityMask(handle, all_processors_mask)
            win32api.CloseHandle(handle)
        except Exception as e:
            continue


number_of_processors = get_number_of_processors()
all_processors_mask = 2 ** number_of_processors - 1
half_processors_mask = 2 ** (number_of_processors // 2) - 1
otherwise_processors_mask = all_processors_mask ^ half_processors_mask
