import tkinter as tk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
import time

class TimeBoxApp:
    def __init__(self, master):
        self.master = master
        master.title("⏱️ Time Box")

        self.task_label = tk.Label(master, text="Task Name:")
        self.task_label.grid(row=0, column=0, sticky="w")

        self.task_entry = tk.Entry(master, width=40)
        self.task_entry.grid(row=0, column=1, pady=5)

        self.dod_label = tk.Label(master, text="Definition of Done (one per line):")
        self.dod_label.grid(row=1, column=0, sticky="nw")

        self.dod_text = ScrolledText(master, width=30, height=6)
        self.dod_text.grid(row=1, column=1, pady=5)

        self.time_label = tk.Label(master, text="Time Limit (minutes):")
        self.time_label.grid(row=2, column=0, sticky="w")

        self.time_entry = tk.Entry(master, width=10)
        self.time_entry.grid(row=2, column=1, sticky="w", pady=5)

        self.start_button = tk.Button(master, text="Start Time Box", command=self.start_timebox)
        self.start_button.grid(row=3, column=0, columnspan=2, pady=10)

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
        timer_win.title(f"🔖 {task}")

        task_label = tk.Label(timer_win, text=f"Task: {task}", font=("Helvetica", 14, "bold"))
        task_label.pack(pady=5)

        countdown_label = tk.Label(timer_win, text="", font=("Helvetica", 24))
        countdown_label.pack(pady=10)

        # Only create DoD frame and checkboxes if there are non-empty DoD lines
        dod_lines = [line for line in dod_lines if line.strip()]
        if dod_lines:
            dod_frame = tk.Frame(timer_win)
            dod_frame.pack(pady=5)

            self.dod_vars = []
            for dod_item in dod_lines:
                var = tk.BooleanVar()
                chk = tk.Checkbutton(dod_frame, text=dod_item, variable=var, anchor="w", justify="left")
                chk.pack(fill="x", anchor="w")
                self.dod_vars.append(var)

        self.run_timer(minutes * 60, countdown_label)

    def run_timer(self, remaining, label):
        mins, secs = divmod(int(remaining), 60)
        label.config(text=f"{mins:02d}:{secs:02d}")
        if remaining > 0:
            label.after(1000, self.run_timer, remaining - 1, label)
        else:
            self.master.bell()  # Plays system beep sound
            messagebox.showinfo("⏰ Time Box Done", "Your time box has ended!")

    def clear_form(self):
        self.task_entry.delete(0, tk.END)
        self.dod_text.delete("1.0", tk.END)
        self.time_entry.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = TimeBoxApp(root)
    root.mainloop()
