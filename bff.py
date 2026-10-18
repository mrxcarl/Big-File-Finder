import os
import subprocess
import webbrowser
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from concurrent.futures import ThreadPoolExecutor
import time

# --- Configuration ---
AUTHOR = "Created by JethroTeK"
GITHUB_URL = "https://github.com/mrxcarl"
# --- Theme Colors ---
BG_DARK = "#1e1e1e"
TEXT_LIGHT = "#e0e0e0"
ACCENT_RED = "#ff4444"
TREE_BG = "#2d2d2d"
TREE_HEADER = "#3d3d3d"

def get_size_mb(size):
    return f"{size / (1024 * 1024):.2f} MB"

# --- Logic ---
def scan_directory():
    folder = filedialog.askdirectory()
    if not folder:
        return

    # UI Reset
    results.delete(*results.get_children())
    status_label.config(text="Initializing Scan...", fg=ACCENT_RED)
    # Reset progress bar to 0
    progress_bar.configure(0)

    # Start the scan in a background thread
    threading.Thread(target=run_multi_threaded_scan, args=(folder,), daemon=True).start()

def run_multi_threaded_scan(base_path):
    file_list = []
    total_size = 0

    try:
        def fast_scan(path):
            items = []
            total = 0
            stack = [path]
            while stack:
                curr_path = stack.pop()
                try:
                    for entry in os.scandir(curr_path):
                        if entry.is_file():
                            items.append((entry.path, entry.stat().st_size))
                            total += entry.stat().st_size
                        elif entry.is_dir():
                            stack.append(entry.path)
                except:
                    pass
            return items, total

        # Step 1: The "Pre-scan" / Discovery phase
        root.after(0, lambda: status_label.config(text="Scanning Files...", fg=ACCENT_RED))
        results_data, final_size = fast_scan(base_path)

        # Sort results by size descending
        results_data.sort(key=lambda x: x[1], reverse=True)

        # Step 2: Update UI and Update Progress Bar
        # We use a loop to update the progress bar as the UI populates
        def update_ui_in_chunks(data, total_sz):
            global last_results
            last_results = data
            
            # Progress Bar logic: 
            # Since we have the full list now, we can show progress as we populate the Treeview
            total_items = len(data)
            for i, (path, size) in enumerate(data[:100]):
                results.insert("", "end", values=(path, get_size_mb(size)))
                # Update progress bar based on index progress (up to 100 items)
                prog_val = (i / 100) * 100 if total_items > 100 else (i / total_items) * 100
                root.after(0, lambda v=prog_val: progress_bar.configure(v))
            
            total_label.config(text=f"Total Folder Size: {get_size_mb(total_sz)}")
            status_label.config(text="Done", fg=ACCENT_RED)

        root.after(0, lambda: update_ui_in_chunks(results_data, final_size))

    except Exception as e:
        root.after(0, lambda: messagebox.showerror("Error", str(e)))
        root.after(0, lambda: status_label.config(text="Error", fg="yellow"))
    finally:
        # Ensure status shows done even if error occurs
        root.after(0, lambda: status_label.config(text="Done", fg=ACCENT_RED))

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

    item_id = selected[0]
    file_path = results.item(item_id)["values"][0]
    file_path = file_path.strip('"').strip("'")

    try:
        folder_path = os.path.dirname(file_path)
        if os.path.exists(folder_path):
            os.startfile(folder_path)
        else:
            if os.path.exists(file_path):
                os.startfile(file_path)
            else:
                messagebox.showwarning("Path Not Found", f"Could not find path:\n{folder_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Could not open folder: {e}")

def copy_path():
    selected = results.selection()
    if not selected:
        return
    file_path = results.item(selected[0])["values"][0]
    root.clipboard_clear()
    root.clipboard_append(file_path)
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
        messagebox.showerror("Error", f"Could not delete: {e}")

def open_github(event=None):
    webbrowser.open(GITHUB_URL)

# --- Custom Progress Bar ---
class RedProgress(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.canvas = tk.Canvas(self, height=20, bg=BG_DARK, highlightthickness=0)
        self.canvas.pack(fill=tk.X)
        self.rect = self.canvas.create_rectangle(0, 0, 0, 20, fill=ACCENT_RED, outline="")
        self.width = 400 # Note: You might want to adjust this or use a dynamic width based on parent

    def configure(self, value):
        val = max(0, min(100, float(value)))
        x_pos = (val / 100) * self.width
        self.canvas.coords(self.rect, 0, 0, x_pos, 20)

# --- GUI Construction ---
root = tk.Tk()
root.title("Big File Finder - JethroTeK")
root.geometry("900x700")
root.configure(bg=BG_DARK)

try:
    root.iconbitmap("bff.ico")
except:
    pass

frame = tk.Frame(root, bg=BG_DARK)
frame.pack(pady=10)
scan_btn = tk.Button(frame, text="Select Folder & Scan", command=scan_directory, bg="#444", fg="white")
scan_btn.pack(side=tk.LEFT, padx=10)
export_btn = tk.Button(frame, text="Export Results", command=export_results, bg="#444", fg="white")
export_btn.pack(side=tk.LEFT, padx=10)
open_btn = tk.Button(frame, text="Open Directory", command=open_directory, bg="#444", fg="white")
open_btn.pack(side=tk.LEFT, padx=10)

# Progress Bar
progress_bar = RedProgress(root)
progress_bar.pack(pady=5)

# Treeview Style Setup
style = ttk.Style()
style.theme_use('clam')
style.configure("Treeview",
                 background=TREE_BG,
                 foreground=TEXT_LIGHT,
                 font=('Segoe UI', 10),
                 field_background=TREE_BG)
style.configure("Treeview.Heading",
                 background=TREE_HEADER,
                 foreground=TEXT_LIGHT,
                 font=('Segoe UI', 11, 'bold'))

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

total_label = tk.Label(root, text="Total Folder Size: 0 MB", bg=BG_DARK, fg=TEXT_LIGHT)
total_label.pack()
status_label = tk.Label(root, text="Idle", bg=BG_DARK, fg=TEXT_LIGHT)
status_label.pack(pady=5)

credit_frame = tk.Frame(root, bg=BG_DARK)
credit_frame.pack(pady=5)
credit_label = tk.Label(credit_frame, text=AUTHOR, bg=BG_DARK, fg=TEXT_LIGHT, font=("Arial", 10, "italic"))
credit_label.pack(side=tk.LEFT, padx=5)
github_label = tk.Label(credit_frame, text="GitHub", fg=ACCENT_RED, bg=BG_DARK, cursor="hand2")
github_label.pack(side=tk.LEFT)
github_label.bind("<Button-1>", open_github)

last_results = []
root.mainloop()