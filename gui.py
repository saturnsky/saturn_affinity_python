import os
import tkinter as tk
import time

import saturn_affinity_lib as sal


class App(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master

        self.master.title("Saturn Affinity")
        self.master.geometry("640x720")
        self.master.resizable(True, True)
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

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

        self.refresh_btn = tk.Button(self.btn_frame, text="Refresh", command=self.processes_update)
        self.refresh_btn.pack(side="left", expand=True, fill="x")

        self.add_btn = tk.Button(self.btn_frame, text="Add", command=self.add_game_item)
        self.add_btn.pack(side="left", expand=True, fill="x")

        self.delete_btn = tk.Button(self.btn_frame, text="Delete", command=self.delete_game_item)
        self.delete_btn.pack(side="right", expand=True, fill="x")

        self.action_frame = tk.Frame(self.master)
        self.action_frame.grid(row=3, column=0, sticky="nsew", columnspan=2)

        self.action_label_disable_text = "Normal Mode. The process affinity setting has been turned off."
        self.action_label_error_text = "Error. This CPU is not supported"

        self.action_label = tk.Label(self.action_frame, text=self.action_label_disable_text)
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
        if sal.get_cpu_support_type() is None:
            self.action_label.config(text=self.action_label_error_text)
        else:
            self.periodic_update()

    def processes_update(self):
        self.current_windows = sal.get_all_windows()
        self.process_listbox.delete(0, tk.END)
        for idx, window in enumerate(self.current_windows):
            self.process_listbox.insert(idx, "{} ({})".format(window[2], window[1].split('\\')[-1]))

    def load_game_list(self):
        self.game_list = []
        self.game_set = set()
        if os.path.exists("game_list.txt"):
            self.game_listbox.delete(0, tk.END)
            with open("game_list.txt", "r", encoding="utf-8") as f:
                raw_data = f.read().splitlines()
                for line in raw_data:
                    program_path, program_name = line.split('|', 1)
                    self.game_list.append((program_path, program_name))
                    self.game_listbox.insert(tk.END, "{} ({})".format(program_name, program_path.split('\\')[-1]))
                    self.game_set.add(program_path)

    def save_game_list(self):
        with open("game_list.txt", "w", encoding="utf-8") as f:
            for game in self.game_list:
                f.write("{}|{}\n".format(game[0], game[1]))

    def add_game_item(self):
        if not self.process_listbox.curselection():
            return
        selected_window = self.current_windows[self.process_listbox.curselection()[0]]
        if selected_window[1] in self.game_set:
            return
        self.game_listbox.insert(tk.END, "{} ({})".format(selected_window[2], selected_window[1].split('\\')[-1]))
        self.game_list.append((selected_window[1], selected_window[2]))
        self.save_game_list()
        self.game_set.add(selected_window[1])

    def delete_game_item(self):
        if not self.game_listbox.curselection():
            return
        selected_game = self.game_listbox.curselection()[0]
        self.game_set.remove(self.game_list[selected_game][0])
        self.game_listbox.delete(selected_game)
        del self.game_list[selected_game]
        self.save_game_list()

    def periodic_update(self):
        current_process = sal.get_current_process()

        if current_process is None:
            self.after(1000, self.periodic_update)
            return
        if current_process[1] in self.game_set:
            if self.current_game != current_process[1] or time.time() - self.previous_update > 60 * 5:
                if self.current_game != current_process[1]:
                    if sal.get_cpu_support_type() == "AMD":
                        self.action_label.config(
                            text="Number of exclusive threads: {} Exclusive L3 cache size: {}MB\n"
                                 "Enable the process affinity setting for {}.".format(sal.get_best_cluster_thread_count(),
                                                                                      sal.get_best_cluster_cache_size('MB'),
                                                                                      current_process[2]))
                    else:
                        self.action_label.config(
                            text="Number of exclusive threads: {} (P-cores Only)\n"
                                 "Enable the process affinity setting for {}.".format(sal.get_best_cluster_thread_count(),
                                                                                      current_process[2]))

                self.current_game = current_process[1]
                sal.set_affinity_all_process(current_process[0])
                self.previous_update = time.time()
        else:
            if self.current_game:
                self.current_game = None
                sal.set_affinity_all_process()
                self.action_label.config(text=self.action_label_disable_text)
        self.after(1000, self.periodic_update)

    def on_closing(self):
        sal.set_affinity_all_process()
        self.master.destroy()


app = App(master=tk.Tk())
app.mainloop()
