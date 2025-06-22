import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
from tkinter.scrolledtext import ScrolledText
import json
import os

# -------------------------------------------------------------
# CONFIG & CONSTANTS
# -------------------------------------------------------------
CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".timebox_config.json")
DEFAULT_CONTEXTS_DIR = os.path.join(os.path.expanduser("~"), ".timebox_contexts")
DEFAULT_CONTEXT = "default"

# -------------------------------------------------------------
# MAIN APPLICATION CLASS
# -------------------------------------------------------------
class TimeBoxApp:
    def __init__(self, master: tk.Tk):
        self.master = master
        master.title("\u23f1 TimeBox")

        # -----------------------
        # Contexts housekeeping
        # -----------------------
        os.makedirs(DEFAULT_CONTEXTS_DIR, exist_ok=True)
        self.load_config()  # sets self.contexts_dir & self.current_context
        self.presets = self.load_presets()
        self.selected_preset: str | None = None

        # -----------------------
        # Menubar UI
        # -----------------------
        self.menu = tk.Menu(master)
        master.config(menu=self.menu)

        self.contexts_dir = self.config.get(
            "contexts_dir",
            os.path.join(os.path.expanduser("~"), ".timebox_contexts")
        )
        os.makedirs(self.contexts_dir, exist_ok=True)

        self.current_context = self.config.get("default_context", "default")

        # --- Contexts menu
        self.context_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Contexts", menu=self.context_menu)
        self.update_context_menu()

        # --- Settings menu
        self.settings_menu = tk.Menu(self.menu, tearoff=0)
        self.settings_menu.add_command(label="Configure Settings", command=self.open_settings_window)
        self.menu.add_cascade(label="Settings", menu=self.settings_menu)

        # -----------------------
        # Form UI
        # -----------------------
        self.task_label = tk.Label(master, text="Task Name:")
        self.task_label.grid(row=0, column=0, sticky="w")

        self.task_entry = tk.Entry(master, width=40)
        self.task_entry.grid(row=0, column=1, pady=5)
        self.task_entry.bind("<KeyRelease>", self.update_action_buttons)

        self.dod_label = tk.Label(master, text="Definition of Done (one per line):")
        self.dod_label.grid(row=1, column=0, sticky="nw")

        self.dod_text = ScrolledText(master, width=30, height=6)
        self.dod_text.grid(row=1, column=1, pady=5)
        self.dod_text.bind("<KeyRelease>", self.update_action_buttons)

        self.time_label = tk.Label(master, text="Time Limit (minutes):")
        self.time_label.grid(row=2, column=0, sticky="w")

        self.time_entry = tk.Entry(master, width=10)
        self.time_entry.grid(row=2, column=1, sticky="w", pady=5)
        self.time_entry.bind("<KeyRelease>", self.update_action_buttons)

        # Action buttons row
        self.start_button = tk.Button(master, text="Start Time Box", command=self.start_timebox)
        self.start_button.grid(row=3, column=0, pady=10)

        self.save_update_button = tk.Button(master, text="Save Preset", command=self.save_or_update_preset)
        self.save_update_button.grid(row=3, column=1, sticky="w", pady=10)

        self.delete_button = tk.Button(master, text="Delete", command=self.delete_preset)
        self.delete_button.grid(row=3, column=1, pady=10)
        self.delete_button.grid_remove()

        self.cancel_button = tk.Button(master, text="Cancel", command=self.clear_form)
        self.cancel_button.grid(row=3, column=1, sticky="e", pady=10)

        # Preset list
        self.preset_label = tk.Label(master, text="Presets:")
        self.preset_label.grid(row=0, column=2, sticky="nw", padx=(20, 0))

        preset_frame = tk.Frame(master)
        preset_frame.grid(row=1, column=2, rowspan=3, padx=(20, 10), pady=5, sticky="n")

        self.preset_scrollbar = tk.Scrollbar(preset_frame, orient="vertical")
        self.preset_listbox = tk.Listbox(preset_frame, height=6, yscrollcommand=self.preset_scrollbar.set)
        self.preset_scrollbar.config(command=self.preset_listbox.yview)
        self.preset_scrollbar.pack(side="right", fill="y")
        self.preset_listbox.pack(side="left", fill="both", expand=True)
        self.preset_listbox.bind("<<ListboxSelect>>", self.load_selected_preset)

        # Initial state
        self.refresh_preset_list()
        self.update_action_buttons()

    # ---------------------------------------------------------
    # CONTEXT MANAGEMENT
    # ---------------------------------------------------------
    def update_context_menu(self):
        """Re-populate the Contexts drop-down each time something changes."""
        # remove everything first
        self.context_menu.delete(0, "end")

        # static items at the top
        self.context_menu.add_command(label="New",  command=self.create_new_context)
        self.context_menu.add_command(label="Rename",      command=self.rename_context)
        self.context_menu.add_command(label="Delete",      command=self.delete_context)
        self.context_menu.add_command(
                    label="Make default",
                    command=self.set_default_context
        )
        self.context_menu.add_separator()

        # gather every *.json in the contexts directory
        context_files = [
            os.path.splitext(f)[0]      # strip “.json”
            for f in os.listdir(self.contexts_dir)
            if f.endswith(".json")
        ]
        if not context_files:  # first-run safety
            context_files = ["default"]

        # make a StringVar so Tk can show the ✓ mark
        if not hasattr(self, "context_var"):
            self.context_var = tk.StringVar()
        self.context_var.set(self.current_context)

        # one radio-button per context
        for ctx in sorted(context_files):
            self.context_menu.add_radiobutton(
                label=ctx,
                variable=self.context_var,
                value=ctx,
                command=lambda c=ctx: self.switch_context(c),
            )
    def switch_context(self, ctx_name: str):
        """Load presets for the chosen context and refresh UI."""
        if ctx_name == self.current_context:
            return
        self.current_context = ctx_name
        self.presets = self.load_presets()      # will read <ctx>.json
        self.refresh_preset_list()
        self.clear_form()
        self.update_context_menu()              # repaint ✓ mark

    def create_new_context(self):
        name = simpledialog.askstring("New Context", "Context name:")
        if not name:
            return
        # create empty JSON file
        path = os.path.join(self.contexts_dir, f"{name}.json")
        if os.path.exists(path):
            messagebox.showerror("Exists", "That context already exists.")
            return
        with open(path, "w") as f:
            json.dump({}, f)
        self.switch_context(name)

    def set_default_context(self):
        self.config["default_context"] = self.current_context
        self.save_config()
        messagebox.showinfo("Default Context",
                            f"'{self.current_context}' is now the default.")
        
    def rename_context(self):
        """Prompt for a new name and rename the context’s JSON file."""
        new_name = simpledialog.askstring("Rename Context",
                                        f"Rename context:",
                                        initialvalue=self.current_context
        )
        if not new_name or new_name == self.current_context:
            return

        old_path = os.path.join(self.contexts_dir, f"{self.current_context}.json")
        new_path = os.path.join(self.contexts_dir, f"{new_name}.json")

        if os.path.exists(new_path) and new_name != self.current_context:
            messagebox.showerror("Exists", "A context with that name already exists.")
            return

        try:
            os.rename(old_path, new_path)
        except OSError as err:
            messagebox.showerror("Error", f"Could not rename file:\n{err}")
            return

        # update runtime state + config if needed
        if self.config.get("default_context") == self.current_context:
            self.config["default_context"] = new_name
            self.save_config()

        self.current_context = new_name
        self.update_context_menu()

    def delete_context(self):
        """Delete the current context (after confirmation)."""
        if self.current_context == self.config.get("default_context", DEFAULT_CONTEXT):
            messagebox.showinfo("Protected", "The default context cannot be deleted.")
            return

        if not messagebox.askyesno("Delete Context",
                                f"Delete context '{self.current_context}'?\n"
                                "Presets in this file will be lost."):
            return

        path = os.path.join(self.contexts_dir, f"{self.current_context}.json")
        try:
            os.remove(path)
        except OSError as err:
            messagebox.showerror("Error", f"Could not delete file:\n{err}")
            return

        # choose a fallback context
        remaining = [f[:-5] for f in os.listdir(self.contexts_dir) if f.endswith(".json")]
        self.current_context = remaining[0] if remaining else "default"
        self.update_context_menu()
        self.presets = self.load_presets()  # reload presets for new context
        self.refresh_preset_list()
        self.clear_form()


    # ---------------------------------------------------------
    # CONFIG FILES
    # ---------------------------------------------------------
    def load_config(self):
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r") as f:
                self.config = json.load(f)
        else:
            self.config = {
                "contexts_dir": DEFAULT_CONTEXTS_DIR,
                "default_context": DEFAULT_CONTEXT,
            }
            self.save_config()

        # Apply config
        self.contexts_dir = self.config.get("contexts_dir", DEFAULT_CONTEXTS_DIR)
        os.makedirs(self.contexts_dir, exist_ok=True)
        self.current_context = self.config.get("default_context", DEFAULT_CONTEXT)

    def save_config(self):
        with open(CONFIG_PATH, "w") as f:
            json.dump(self.config, f, indent=2)

    # ---------------------------------------------------------
    # PRESET FILE I/O PER CONTEXT
    # ---------------------------------------------------------
    def context_file(self):
        return os.path.join(self.contexts_dir, f"{self.current_context}.json")

    def load_presets(self):
        path = self.context_file()
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
        return {}

    def save_presets(self):
        path = self.context_file()
        with open(path, "w") as f:
            json.dump(self.presets, f, indent=2)

    # ---------------------------------------------------------
    # PRESET LIST OPERATIONS
    # ---------------------------------------------------------
    def refresh_preset_list(self):
        self.preset_listbox.delete(0, tk.END)
        for name in sorted(self.presets):
            self.preset_listbox.insert(tk.END, name)
        self.selected_preset = None
        self.delete_button.grid_remove()
        self.update_action_buttons()

    def load_selected_preset(self, _event=None):
        sel = self.preset_listbox.curselection()
        if not sel:
            return
        name = self.preset_listbox.get(sel[0])
        data = self.presets[name]
        self.selected_preset = name
        # Populate form
        self.task_entry.delete(0, tk.END)
        self.task_entry.insert(0, data["task"])
        self.dod_text.delete("1.0", tk.END)
        # Add dash prefix for each line
        self.dod_text.insert(tk.END, "\n".join(f"- {line}" for line in data["dod"]))
        self.time_entry.delete(0, tk.END)
        self.time_entry.insert(0, str(data["minutes"]))
        self.update_action_buttons()

    def save_or_update_preset(self):
        task = self.task_entry.get().strip()
        dod_raw = self.dod_text.get("1.0", tk.END).strip().split("\n")
        # Strip the leading dash, if present
        dod = [line.lstrip("-").strip() for line in dod_raw if line.strip()]

        try:
            minutes = float(self.time_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number for minutes.")
            return

        if not task:
            messagebox.showerror("Missing Task", "Please enter a task name.")
            return

        # Update or create
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
        if messagebox.askyesno("Delete Preset", f"Delete preset '{self.selected_preset}'?"):
            del self.presets[self.selected_preset]
            self.save_presets()
            self.refresh_preset_list()
            self.clear_form()

    # ---------------------------------------------------------
    # ACTION-BUTTON ENABLE / DISABLE
    # ---------------------------------------------------------
    def update_action_buttons(self, _event=None):
        task_filled = bool(self.task_entry.get().strip())
        dod_filled = bool(self.dod_text.get("1.0", tk.END).strip())
        time_filled = bool(self.time_entry.get().strip())

        if task_filled or dod_filled or time_filled:
            # Show Save/Update
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

    # ---------------------------------------------------------
    # TIMER LOGIC
    # ---------------------------------------------------------
    def start_timebox(self):
        task = self.task_entry.get().strip()
        dod_raw = self.dod_text.get("1.0", tk.END).strip().split("\n")
        dod_lines = [line.lstrip("-").strip() for line in dod_raw if line.strip()]

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

    def show_timer_window(self, task: str, dod_lines: list[str], minutes: float):
        timer_win = tk.Toplevel(self.master)
        timer_win.geometry("400x300")
        timer_win.title(f"\U0001F516 {task}")

        tk.Label(timer_win, text=task, font=("Helvetica", 14, "bold")).pack(pady=5)

        countdown_label = tk.Label(timer_win, text="", font=("Helvetica", 24))
        countdown_label.pack(pady=10)

        # DoD checklist
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

        self.run_timer(int(minutes * 60), countdown_label)

    # ------------------- color helpers -----------------------
    def update_dod_color(self, label: tk.Label, var: tk.BooleanVar):
        label.config(fg="green" if var.get() else "red")

    # ------------------- running timer -----------------------
    def run_timer(self, remaining: int, label: tk.Label):
        mins, secs = divmod(remaining, 60)
        label.config(text=f"{mins:02d}:{secs:02d}")

        if remaining <= 300:  # 5 minutes or less
            label.config(fg="red")
        if remaining > 0:
            label.after(1000, self.run_timer, remaining - 1, label)
        else:
            self.master.bell()
            messagebox.showinfo("\u23F0 Time Box Done", "Your time box has ended!")

    # ---------------------------------------------------------
    # DoD TEXT SHORTCUTS
    # ---------------------------------------------------------
    def handle_dod_newline(self, _event):
        self.dod_text.insert(tk.INSERT, "\n- ")
        return "break"  # prevent default newline

    def insert_dash_on_focus(self, _event):
        if not self.dod_text.get("1.0", tk.END).strip():
            self.dod_text.insert("1.0", "- ")

    # ---------------------------------------------------------
    # HOUSEKEEPING
    # ---------------------------------------------------------
    def clear_form(self):
        self.task_entry.delete(0, tk.END)
        self.dod_text.delete("1.0", tk.END)
        self.time_entry.delete(0, tk.END)
        self.selected_preset = None
        self.update_action_buttons()

    # ---------------------------------------------------------
    # SETTINGS WINDOW
    # ---------------------------------------------------------
    def open_settings_window(self):
        win = tk.Toplevel(self.master)
        win.title("Settings")

        tk.Label(win, text="Contexts Folder:").pack(pady=5)
        path_entry = tk.Entry(win, width=50)
        path_entry.insert(0, self.contexts_dir)
        path_entry.pack(pady=5)

        def browse():
            path = filedialog.askdirectory()
            if path:
                path_entry.delete(0, tk.END)
                path_entry.insert(0, path)

        tk.Button(win, text="Browse", command=browse).pack(pady=5)

        def save():
            new_dir = path_entry.get().strip()
            if not new_dir:
                messagebox.showerror("Error", "Path cannot be empty.")
                return
            os.makedirs(new_dir, exist_ok=True)
            self.config["contexts_dir"] = new_dir
            self.save_config()
            self.contexts_dir = new_dir
            self.update_context_menu()
            win.destroy()

        tk.Button(win, text="Save", command=save).pack(pady=10)

# -------------------------------------------------------------
# LAUNCH
# -------------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = TimeBoxApp(root)
    root.mainloop()
