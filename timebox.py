import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
from tkinter.scrolledtext import ScrolledText
import time
import json
import os

CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".timebox_config.json")

class TimeBoxApp:
    def __init__(self, master):
        self.master = master
        master.title("\u23f1\ufe0f Time Box")

        self.load_config()
        self.presets = self.load_presets()
        self.selected_preset = None

        self.menu = tk.Menu(master)
        master.config(menu=self.menu)
        file_menu = tk.Menu(self.menu, tearoff=0)
        file_menu.add_command(label="Settings", command=self.open_settings_window)
        self.menu.add_cascade(label="File", menu=file_menu)

        self.task_label = tk.Label(master, text="Task Name:")
        self.task_label.grid(row=0, column=0, sticky="w")

        self.task_entry = tk.Entry(master, width=40)
        self.task_entry.grid(row=0, column=1, pady=5)
        self.task_entry.bind("<KeyRelease>", self.update_action_buttons)

        self.dod_label = tk.Label(master, text="DoD Items (one per line):")
        self.dod_label.grid(row=1, column=0, sticky="nw")

        self.dod_text = ScrolledText(master, width=30, height=6)
        self.dod_text.grid(row=1, column=1, pady=5)
        self.dod_text.bind("<KeyRelease>", self.update_action_buttons)

        self.time_label = tk.Label(master, text="Time Limit (minutes):")
        self.time_label.grid(row=2, column=0, sticky="w")

        self.time_entry = tk.Entry(master, width=10)
        self.time_entry.grid(row=2, column=1, sticky="w", pady=5)
        self.time_entry.bind("<KeyRelease>", self.update_action_buttons)

        self.start_button = tk.Button(master, text="Start Time Box", command=self.start_timebox)
        self.start_button.grid(row=3, column=0, pady=10)

        self.save_update_button = tk.Button(master, text="Save Preset", command=self.save_or_update_preset)
        self.save_update_button.grid(row=3, column=1, pady=10, sticky="w")

        self.delete_button = tk.Button(master, text="Delete", command=self.delete_preset)
        self.delete_button.grid(row=3, column=1, pady=10)
        self.delete_button.grid_remove()

        self.cancel_button = tk.Button(master, text="Cancel", command=self.clear_form)
        self.cancel_button.grid(row=3, column=1, pady=10, sticky="e")

        self.preset_label = tk.Label(master, text="Presets:")
        self.preset_label.grid(row=0, column=2, sticky="nw", padx=(20, 0))

        preset_frame = tk.Frame(master)
        preset_frame.grid(row=1, column=2, rowspan=3, padx=(20, 10), pady=5, sticky="n")

        self.preset_scrollbar = tk.Scrollbar(preset_frame, orient="vertical")
        self.preset_listbox = tk.Listbox(preset_frame, height=6, yscrollcommand=self.preset_scrollbar.set)
        self.preset_scrollbar.config(command=self.preset_listbox.yview)
        self.preset_scrollbar.pack(side="right", fill="y")
        self.preset_listbox.pack(side="left", fill="both", expand=True)
        self.preset_listbox.bind('<<ListboxSelect>>', self.load_selected_preset)

        self.refresh_preset_list()
        self.update_action_buttons()

    def load_config(self):
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r") as f:
                self.config = json.load(f)
        else:
            self.config = {"presets_file": os.path.join(os.path.expanduser("~"), "timebox_presets.json")}
            self.save_config()

    def save_config(self):
        with open(CONFIG_PATH, "w") as f:
            json.dump(self.config, f, indent=2)

    def load_presets(self):
        if os.path.exists(self.config["presets_file"]):
            with open(self.config["presets_file"], "r") as f:
                return json.load(f)
        return {}

    def save_presets(self):
        with open(self.config["presets_file"], "w") as f:
            json.dump(self.presets, f, indent=2)

    def refresh_preset_list(self):
        self.preset_listbox.delete(0, tk.END)
        for name in self.presets:
            self.preset_listbox.insert(tk.END, name)
        self.selected_preset = None
        self.delete_button.grid_remove()
        self.update_action_buttons()

    def load_selected_preset(self, event):
        selection = self.preset_listbox.curselection()
        if not selection:
            return
        name = self.preset_listbox.get(selection[0])
        data = self.presets[name]
        self.task_entry.delete(0, tk.END)
        self.task_entry.insert(0, data["task"])
        self.dod_text.delete("1.0", tk.END)
        self.dod_text.insert(tk.END, "\n".join(data["dod"]))
        self.time_entry.delete(0, tk.END)
        self.time_entry.insert(0, str(data["minutes"]))
        self.selected_preset = name
        self.update_action_buttons()

    def save_or_update_preset(self):
        task = self.task_entry.get().strip()
        dod = self.dod_text.get("1.0", tk.END).strip().split("\n")
        try:
            minutes = float(self.time_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number for minutes.")
            return

        if self.selected_preset:
            self.presets[self.selected_preset] = {"task": task, "dod": dod, "minutes": minutes}
        else:
            name = simpledialog.askstring("Preset Name", "Enter a name for this preset:")
            if not name:
                return
            self.presets[name] = {"task": task, "dod": dod, "minutes": minutes}
        self.save_presets()
        self.refresh_preset_list()

    def delete_preset(self):
        if not self.selected_preset:
            return
        confirm = messagebox.askyesno("Delete Preset", f"Are you sure you want to delete '{self.selected_preset}'?")
        if confirm:
            del self.presets[self.selected_preset]
            self.save_presets()
            self.refresh_preset_list()
            self.clear_form()

    def update_action_buttons(self, event=None):
        task = self.task_entry.get().strip()
        dod = self.dod_text.get("1.0", tk.END).strip()
        time_text = self.time_entry.get().strip()

        if task or dod or time_text:
            if self.selected_preset:
                self.save_update_button.config(text="Update Preset")
                self.delete_button.grid()
            else:
                self.save_update_button.config(text="Save Preset")
                self.delete_button.grid_remove()
            self.save_update_button.grid()
        else:
            self.save_update_button.grid_remove()
            self.delete_button.grid_remove()

    def start_timebox(self):
        task = self.task_entry.get().strip()
        dod_lines = self.dod_text.get("1.0", tk.END).strip().split("\n")
        try:
            minutes = float(self.time_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number for minutes.")
            return

        if not task:
            messagebox.showerror("Missing Task", "Please enter a task name.")
            return

        self.show_timer_window(task, dod_lines, minutes)
        self.clear_form()

    def show_timer_window(self, task, dod_lines, minutes):
        timer_win = tk.Toplevel(self.master)
        timer_win.geometry("400x300")
        timer_win.title(f"\ud83d\udd16 {task}")

        task_label = tk.Label(timer_win, text=f"{task}", font=("Helvetica", 14, "bold"))
        task_label.pack(pady=5)

        countdown_label = tk.Label(timer_win, text="", font=("Helvetica", 24))
        countdown_label.pack(pady=10)

        dod_lines = [line for line in dod_lines if line.strip()]
        dod_frame = tk.Frame(timer_win)
        dod_frame.pack(pady=5)

        self.dod_vars = []
        self.dod_checks = []
        for dod_item in dod_lines:
            var = tk.BooleanVar()
            row = tk.Frame(dod_frame)
            row.pack(anchor="w", pady=2)

            chk = tk.Checkbutton(row, variable=var)
            chk.pack(side="left")

            label = tk.Label(row, text=dod_item, anchor="w", justify="left")
            label.pack(side="left", padx=5)
            label.config(fg="red")

            chk.config(command=lambda v=var, l=label: self.update_dod_color(l, v))

            self.dod_vars.append(var)
            self.dod_checks.append((chk, label))

        self.run_timer(minutes * 60, countdown_label, task_label)

    def update_dod_color(self, label, var):
        if var.get():
            label.config(fg="green")
        else:
            label.config(fg="red")

    def run_timer(self, remaining, label, task_label):
        mins, secs = divmod(int(remaining), 60)
        label.config(text=f"{mins:02d}:{secs:02d}")

        if remaining <= 300:
            label.config(fg="red")

        if remaining > 0:
            label.after(1000, self.run_timer, remaining - 1, label, task_label)
        else:
            self.master.bell()
            messagebox.showinfo("⏰ Time Box Done", "Your time box has ended!")

    def clear_form(self):
        self.task_entry.delete(0, tk.END)
        self.dod_text.delete("1.0", tk.END)
        self.time_entry.delete(0, tk.END)
        self.selected_preset = None
        self.update_action_buttons()

    def open_settings_window(self):
        settings_win = tk.Toplevel(self.master)
        settings_win.title("Settings")

        label = tk.Label(settings_win, text="Presets File Path:")
        label.pack(pady=5)

        path_entry = tk.Entry(settings_win, width=50)
        path_entry.insert(0, self.config["presets_file"])
        path_entry.pack(pady=5)

        def browse():
            path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
            if path:
                path_entry.delete(0, tk.END)
                path_entry.insert(0, path)

        browse_btn = tk.Button(settings_win, text="Browse", command=browse)
        browse_btn.pack(pady=5)

        def save():
            self.config["presets_file"] = path_entry.get().strip()
            self.save_config()
            self.presets = self.load_presets()
            self.refresh_preset_list()
            settings_win.destroy()

        save_btn = tk.Button(settings_win, text="Save", command=save)
        save_btn.pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = TimeBoxApp(root)
    root.mainloop()
