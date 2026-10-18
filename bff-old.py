import os
import subprocess
import webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

AUTHOR = "Created by Jason C. Klein"
GITHUB_URL = "https://github.com/mrxcarl"

def get_size_mb(size):
    return f"{size / (1024 * 1024):.2f} MB"

def scan_directory():
    folder = filedialog.askdirectory()
    if not folder:
        return

    status_label.config(text="Scanning...")
    root.update()

    file_list = []
    total_size = 0

    try:
        for root_dir, _, files in os.walk(folder):
            for file in files:
                try:
                    path = os.path.join(root_dir, file)
                    size = os.path.getsize(path)
                    file_list.append((path, size))
                    total_size += size
                except:
                    pass

        file_list.sort(key=lambda x: x[1], reverse=True)
        results.delete(*results.get_children())

        for path, size in file_list[:100]:
            results.insert("", "end", values=(path, get_size_mb(size)))

        total_label.config(text=f"Total Folder Size: {get_size_mb(total_size)}")
        status_label.config(text="Done")

        global last_results
        last_results = file_list

    except Exception as e:
        messagebox.showerror("Error", str(e))
        status_label.config(text="Error")

def export_results():
    if not last_results:
        messagebox.showinfo("No Data", "Run a scan first.")
        return

    save_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text File", "*.txt")])
    if not save_path:
        return

    with open(save_path, "w", encoding="utf-8") as f:
        for path, size in last_results:
            f.write(f"{get_size_mb(size)} - {path}\n")

    messagebox.showinfo("Saved", "Results exported successfully.")

def open_directory():
    selected = results.selection()
    if not selected:
        messagebox.showinfo("No Selection", "Please select a file first.")
        return

    file_path = results.item(selected[0])["values"][0]
    try:
        subprocess.run(["explorer", f"/select,{file_path}"])
    except Exception as e:
        messagebox.showerror("Error", str(e))

def copy_path():
    selected = results.selection()
    if not selected:
        return
    file_path = results.item(selected[0])["values"][0]
    root.clipboard_clear()
    root.clipboard_append(file_path)
    root.update()
    messagebox.showinfo("Copied", "File path copied to clipboard.")

def delete_file():
    selected = results.selection()
    if not selected:
        return
    file_path = results.item(selected[0])["values"][0]

    confirm = messagebox.askyesno("Delete", f"Delete this file?\n{file_path}")
    if not confirm:
        return

    try:
        os.remove(file_path)
        results.delete(selected[0])
        messagebox.showinfo("Deleted", "File deleted successfully.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def open_github(event=None):
    webbrowser.open(GITHUB_URL)

# ---------------- GUI ---------------- #

root = tk.Tk()
root.title("Big File Finder - Jason C. Klein")
root.geometry("900x560")

frame = tk.Frame(root)
frame.pack(pady=10)

scan_btn = tk.Button(frame, text="Select Folder & Scan", command=scan_directory)
scan_btn.pack(side=tk.LEFT, padx=10)

export_btn = tk.Button(frame, text="Export Results", command=export_results)
export_btn.pack(side=tk.LEFT, padx=10)

open_btn = tk.Button(frame, text="Open Directory", command=open_directory)
open_btn.pack(side=tk.LEFT, padx=10)

columns = ("File Path", "Size")
results = ttk.Treeview(root, columns=columns, show="headings")
results.heading("File Path", text="File Path")
results.heading("Size", text="Size")
results.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Right-click menu
menu = tk.Menu(root, tearoff=0)
menu.add_command(label="Open Directory", command=open_directory)
menu.add_command(label="Copy Path", command=copy_path)
menu.add_command(label="Delete File", command=delete_file)

def show_menu(event):
    row = results.identify_row(event.y)
    if row:
        results.selection_set(row)
        menu.post(event.x_root, event.y_root)

results.bind("<Button-3>", show_menu)

total_label = tk.Label(root, text="Total Folder Size: 0 MB")
total_label.pack()

status_label = tk.Label(root, text="Idle")
status_label.pack(pady=5)

credit_frame = tk.Frame(root)
credit_frame.pack(pady=5)

credit_label = tk.Label(credit_frame, text=AUTHOR, font=("Arial", 10, "italic"))
credit_label.pack(side=tk.LEFT, padx=5)

github_label = tk.Label(credit_frame, text="GitHub", fg="blue", cursor="hand2")
github_label.pack(side=tk.LEFT)
github_label.bind("<Button-1>", open_github)

last_results = []

root.mainloop()