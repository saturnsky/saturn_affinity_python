# -*- coding: utf-8 -*-

import win32process
import win32api
import win32con
import win32gui

import cache_lib

processed_process = None
processed_time = 0
game_only_mode = False
game_set = set()

cpu_support_type = None
l3_cache_clusters = []
best_cluster_mask = 0
otherwise_cluster_mask = 0
all_cluster_mask = 0

best_cluster_thread_count = 0


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
            continue
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
                    if p_name == target_pname:
                        if win32process.GetProcessAffinityMask(handle)[0] != best_cluster_mask:
                            win32process.SetProcessAffinityMask(handle, best_cluster_mask)
                            print("Set affinity to best cluster for %s" % p_name)
                    else:
                        if win32process.GetProcessAffinityMask(handle)[0] != otherwise_cluster_mask:
                            win32process.SetProcessAffinityMask(handle, otherwise_cluster_mask)
                else:
                    if win32process.GetProcessAffinityMask(handle)[0] != all_cluster_mask:
                        win32process.SetProcessAffinityMask(handle, all_cluster_mask)
            win32api.CloseHandle(handle)
        except Exception as e:
            continue


def get_processor_structure():
    infos = cache_lib.GetLogicalProcessorInformation()
    cache_clusters = []

    smt_mask = 0
    non_smt_mask = 0

    for info in infos:
        if info.Relationship == 2:  # RelationCache
            if info.Cache.Level == 3:
                cache_clusters.append((info.ProcessorMask, info.Cache.Size))
        elif info.Relationship == 0:  # RelationProcessorCore
            if bin(info.ProcessorMask).count('1') > 1:
                smt_mask |= info.ProcessorMask
            else:
                non_smt_mask |= info.ProcessorMask

    cache_clusters = sorted(cache_clusters, key=lambda x: x[1], reverse=True)

    support_type = None
    all_cluster_mask_local = 0
    best_cluster_mask_local = 0
    otherwise_cluster_mask_local = 0

    for cluster in cache_clusters:
        all_cluster_mask_local |= cluster[0]

    # Multi Cache Cluster CPU (Supported AMD CPU)
    if len(cache_clusters) > 1:
        support_type = 'AMD'
        best_cluster_mask_local = cache_clusters[0][0]
        otherwise_cluster_mask_local = all_cluster_mask_local - best_cluster_mask_local
    elif smt_mask != all_cluster_mask:
        support_type = 'Intel'
        best_cluster_mask_local = smt_mask
        otherwise_cluster_mask_local = non_smt_mask
    else:
        support_type = None

    return cache_clusters, all_cluster_mask_local, best_cluster_mask_local, otherwise_cluster_mask_local, support_type


# count of core in best cluster
def get_best_cluster_thread_count():
    global best_cluster_thread_count
    if not best_cluster_thread_count:
        best_cluster_thread_count = bin(best_cluster_mask).count('1')
    return best_cluster_thread_count


def get_best_cluster_cache_size(size_unit='MB'):
    if size_unit == 'MB':
        return l3_cache_clusters[0][1] // 1048576
    elif size_unit == 'KB':
        return l3_cache_clusters[0][1] // 1024
    else:
        return l3_cache_clusters[0][1]


# Check supported CPU types
def get_cpu_support_type():
    return cpu_support_type


l3_cache_clusters, all_cluster_mask, best_cluster_mask, otherwise_cluster_mask, cpu_support_type = get_processor_structure()
