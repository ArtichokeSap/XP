import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
from xp_tracker import User, Task
import datetime

user = User()
user.load_from_json("user_data.json")

root = tk.Tk()
root.title("XP Tracker")
root.geometry("1280x720")

font = ("Helvetica", 12)

entry_frame = ttk.Frame(root)
entry_frame.pack(side="left", fill="y", padx=10, pady=10)

# Task entry widgets
title = ttk.Label(entry_frame, text="Add Task", font=("Helvetica", 14, "bold"))
title.pack(pady=5)

desc_label = ttk.Label(entry_frame, text="Description:", font=font)
desc_label.pack(anchor="w")
desc_entry = ttk.Entry(entry_frame, font=font)
desc_entry.pack(fill="x")

cat_label = ttk.Label(entry_frame, text="Category:", font=font)
cat_label.pack(anchor="w")
cat_var = tk.StringVar()
cat_dropdown = ttk.Combobox(entry_frame, textvariable=cat_var, font=font)
cat_dropdown['values'] = ('typing', 'piano', 'reading', 'exercise', 'cleaning')
cat_dropdown.current(0)
cat_dropdown.pack(fill="x")

stat_label = ttk.Label(entry_frame, text="Stat:", font=font)
stat_label.pack(anchor="w")
stat_var = tk.StringVar()
stat_dropdown = ttk.Combobox(entry_frame, textvariable=stat_var, font=font)
stat_dropdown['values'] = ('Body','Mind','Art','Tech','Home','Spirit')
stat_dropdown.current(0)
stat_dropdown.pack(fill="x")

min_label = ttk.Label(entry_frame, text="Minutes:", font=font)
min_label.pack(anchor="w")
min_entry = ttk.Entry(entry_frame, font=font)
min_entry.pack(fill="x")

date_label = ttk.Label(entry_frame, text="Date:", font=font)
date_label.pack(anchor="w")
date_picker = DateEntry(entry_frame, font=font, width=16, background='darkblue', foreground='white', borderwidth=2, firstweekday='sunday')
date_picker.pack(fill="x")

def submit_task():
    try:
        task = Task(
            name=desc_entry.get(),
            category=cat_var.get(),
            duration=int(min_entry.get()),
            stat=stat_var.get(),
            date=date_picker.get_date()
        )
        user.add_task(task)
        user.save_to_json("user_data.json")
        refresh()
    except Exception as e:
        print("Error:", e)

def undo():
    user.undo()
    user.save_to_json("user_data.json")
    refresh()

def refresh():
    stats_label.config(text=f"XP: {user.xp}\nLevel: {user.level}\n" + "\n".join(f"{k}: {v}" for k,v in user.stats.items()))
    task_list.delete(0, tk.END)
    for t in user.tasks[-5:]:
        task_list.insert(tk.END, f"{t.date}: {t.name} ({t.duration}min)")

submit_btn = ttk.Button(entry_frame, text="Submit", command=submit_task, style='Accent.TButton')
submit_btn.pack(pady=10, fill="x")

undo_btn = ttk.Button(entry_frame, text="Undo", command=undo)
undo_btn.pack(pady=5, fill="x")

stats_label = ttk.Label(entry_frame, text="", font=font, justify="left")
stats_label.pack(pady=10)

log_frame = ttk.Frame(root)
log_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

log_title = ttk.Label(log_frame, text="Recent Tasks", font=("Helvetica", 14, "bold"))
log_title.pack(anchor="w")

task_list = tk.Listbox(log_frame, font=font, height=10)
task_list.pack(fill="both", expand=True)

refresh()
root.mainloop()