import os
import sys
import time
import tkinter as tk

import ctypes
import pystray
import win32api
import win32event
import winerror
from PIL import Image

import json

import saturn_affinity_lib as sal


class App(tk.Frame):
    def tray_setup(self):
        tray_menu = (
            pystray.MenuItem("Show", self.on_showing),
            pystray.MenuItem("Quit", self.on_closing),
        )
        self.icon = pystray.Icon(
            name="Saturn Affinity",
            icon=self.default_icon,
            title="Saturn Affinity",
            menu=tray_menu,
        )
        self.icon.run_detached()

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master

        self.default_icon = Image.open(self.resource_path("assets/default.ico"))
        self.active_icon = Image.open(self.resource_path("assets/active.ico"))
        self.icon = None

        self.master.iconbitmap(self.resource_path("assets/default.ico"))

        self.tray_setup()

        self.master.title("Saturn Affinity")
        self.master.geometry("640x720")
        self.master.resizable(True, True)
        self.master.protocol("WM_DELETE_WINDOW", self.hide_tray)

        self.processes_label = tk.Label(self.master, text="Processes")
        self.processes_label.grid(row=0, column=0)

        self.process_listbox = tk.Listbox(self.master)
        self.process_listbox.grid(row=1, column=0, sticky="nsew")

        self.game_label = tk.Label(self.master, text="Game")
        self.game_label.grid(row=0, column=1)

        self.game_listbox = tk.Listbox(self.master)
        self.game_listbox.grid(row=1, column=1, sticky="nsew")

        self.btn_frame = tk.Frame(self.master)
        self.btn_frame.grid(row=2, column=0, sticky="nsew", columnspan=2)

        self.refresh_btn = tk.Button(
            self.btn_frame, text="Refresh", command=self.processes_update
        )
        self.refresh_btn.pack(side="left", expand=True, fill="x")

        self.add_btn = tk.Button(self.btn_frame, text="Add", command=self.add_game_item)
        self.add_btn.pack(side="left", expand=True, fill="x")

        self.delete_btn = tk.Button(
            self.btn_frame, text="Delete", command=self.delete_game_item
        )
        self.delete_btn.pack(side="right", expand=True, fill="x")

        self.action_frame = tk.Frame(self.master)
        self.action_frame.grid(row=3, column=0, sticky="nsew", columnspan=2)

        self.action_label_disable_text = (
            "Normal Mode. The process affinity setting has been turned off."
        )
        self.action_label_error_text = "Error. This CPU is not supported"

        self.action_label = tk.Label(
            self.action_frame, text=self.action_label_disable_text
        )
        self.action_label.pack(side="left", expand=True, fill="both")

        self.master.grid_rowconfigure(1, weight=1)
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_columnconfigure(1, weight=1)
        self.master.grid_rowconfigure(3, minsize=40)
        self.current_windows = []
        self.game_list = []
        self.game_set = set()
        self.current_game = None
        self.previous_update = 0

        self.processes_update()
        self.load_game_list()
        if sal.get_current_cpu_type() == "Normal":
            self.action_label.config(text=self.action_label_error_text)
        else:
            self.periodic_update()

    def processes_update(self):
        self.current_windows = sal.get_windows_info()
        self.process_listbox.delete(0, tk.END)
        for idx, window in enumerate(self.current_windows):
            self.process_listbox.insert(
                idx, "{} ({})".format(window[2], window[1].split("\\")[-1])
            )

    def load_legacy_game_list(self, raw_data):
        for line in raw_data:
            program_path, program_name = line.split("|", 1)
            self.game_list.append(
                {
                    "name": program_name,
                    "path": program_path,
                }
            )
            self.game_listbox.insert(
                tk.END, "{} ({})".format(program_name, program_path.split("\\")[-1])
            )
            self.game_set.add(program_path)

    def load_game_list(self):
        self.game_list = []
        self.game_set = set()
        if os.path.exists("game_list.txt"):
            self.game_listbox.delete(0, tk.END)
            with open("game_list.txt", "r", encoding="utf-8") as f:
                raw_data = f.read().splitlines()
                if not len(raw_data):
                    return
                if "|" in raw_data[0]:  # legacy support
                    self.load_legacy_game_list(raw_data)
                    return
                # The first line contains the version information for the save file.
                for line in raw_data[1:]:
                    game_info = json.loads(line)
                    self.game_list.append(game_info)
                    self.game_listbox.insert(
                        tk.END,
                        "{} ({})".format(
                            game_info["name"], game_info["path"].split("\\")[-1]
                        ),
                    )
                    self.game_set.add(game_info["path"])
                return

    def save_game_list(self):
        with open("game_list.txt", "w", encoding="utf-8") as f:
            f.write("1.0\n")
            for game in self.game_list:
                f.write(json.dumps(game) + "\n")

    def add_game_item(self):
        if not self.process_listbox.curselection():
            return
        selected_window = self.current_windows[self.process_listbox.curselection()[0]]
        if selected_window[1] in self.game_set:
            return
        self.game_listbox.insert(
            tk.END,
            "{} ({})".format(selected_window[2], selected_window[1].split("\\")[-1]),
        )
        self.game_list.append({"name": selected_window[2], "path": selected_window[1]})
        self.save_game_list()
        self.game_set.add(selected_window[1])

    def delete_game_item(self):
        if not self.game_listbox.curselection():
            return
        selected_game = self.game_listbox.curselection()[0]
        self.game_set.remove(self.game_list[selected_game]["path"])
        self.game_listbox.delete(selected_game)
        del self.game_list[selected_game]
        self.save_game_list()

    def active_action(self, current_process):
        if self.current_game != current_process[1]:
            if sal.get_current_cpu_type() == "AMD_MultiCCX":
                self.action_label.config(
                    text="Number of exclusive threads: {} Exclusive L3 cache size: {}MB\n"
                    "Enable the process affinity setting for {}.".format(
                        sal.get_thread_count_in_core_cluster(0),
                        sal.get_cache_size_in_core_cluster(0, "MB"),
                        current_process[2],
                    )
                )
            elif sal.get_current_cpu_type() == "Intel_BigLittle":
                self.action_label.config(
                    text="Number of exclusive threads: {} (P-cores Only)\n"
                    "Enable the process affinity setting for {}.".format(
                        sal.get_thread_count_in_core_cluster(0), current_process[2]
                    )
                )
            self.icon.icon = self.active_icon
            self.master.iconbitmap(self.resource_path("assets/active.ico"))

        self.current_game = current_process[1]
        sal.set_process_affinity_and_priority(current_process[1], cluster_mask=1)

        self.previous_update = time.time()

    def inactive_action(self):
        self.icon.icon = self.default_icon
        self.master.iconbitmap(self.resource_path("assets/default.ico"))
        self.current_game = None
        sal.set_process_affinity_and_priority()
        self.action_label.config(text=self.action_label_disable_text)

    def periodic_update(self):
        current_process = sal.get_foreground_process_info()

        if current_process is None:
            self.after(1000, self.periodic_update)
            return
        if current_process[1] in self.game_set:
            if (
                self.current_game != current_process[1]
                or time.time() - self.previous_update > 60 * 5
            ):
                self.active_action(current_process)
        else:
            if self.current_game:
                self.inactive_action()

        self.after(1000, self.periodic_update)

    def on_closing(self):
        sal.set_process_affinity_and_priority()
        self.icon.stop()
        app.quit()

    @staticmethod
    def resource_path(relative_path):
        if hasattr(sys, "_MEIPASS"):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)

    def on_showing(self):
        self.processes_update()
        self.master.after(0, self.master.deiconify)

    def hide_tray(self):
        self.master.withdraw()


mutex = win32event.CreateMutex(None, 1, "SaturnAffinity")
last_error = win32api.GetLastError()
if last_error == winerror.ERROR_ALREADY_EXISTS:
    mutex = None
    ctypes.windll.user32.MessageBoxW(
        0, "Saturn Affinity is already running.", "Saturn Affinity", 0
    )
    sys.exit(0)

app = App(master=tk.Tk())
app.mainloop()
