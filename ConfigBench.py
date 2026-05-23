
import tkinter as tk
from tkinter import filedialog, messagebox
import re
import os

# --- Globals ---
entries = {}
current_template = ""

TEMPLATE_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")

# --- Load Templates from Folder ---
def get_templates():
    if not os.path.exists(TEMPLATE_FOLDER):
        os.makedirs(TEMPLATE_FOLDER)

    files = [f for f in os.listdir(TEMPLATE_FOLDER) if f.endswith(".txt")]
    return files if files else ["No Templates Found"]

# --- Load Template from Dropdown ---
def load_template(*args):
    global current_template

    filename = template_var.get()
    path = os.path.join(TEMPLATE_FOLDER, filename)

    if os.path.exists(path):
        with open(path, "r") as f:
            current_template = f.read()

        template_text.delete("1.0", tk.END)
        template_text.insert(tk.END, current_template)

        scan_variables()

# --- Scan Variables ---
def scan_variables():
    global entries
    entries.clear()

    # Clear UI
    for widget in variable_frame.winfo_children():
        widget.destroy()

    template = template_text.get("1.0", tk.END)

    # Supports letters, numbers, underscore, dash
    vars_found = sorted(set(re.findall(r"\$([a-zA-Z0-9_-]+)", template)))

    if not vars_found:
        tk.Label(variable_frame, text="No variables found").pack()
        return

    # Create scrollable inputs
    for var in vars_found:
        row = tk.Frame(variable_frame)
        row.pack(fill="x", pady=2)

        label = tk.Label(row, text=var, width=20, anchor="w")
        label.pack(side="left")

        entry = tk.Entry(row)
        entry.pack(side="left", fill="x", expand=True)

        entry.bind("<KeyRelease>", update_preview)

        entries[var] = entry

# --- Generate Output ---
def generate_config():
    output = build_output()

    path = filedialog.asksaveasfilename(defaultextension=".txt")
    if path:
        with open(path, "w") as f:
            f.write(output)

        messagebox.showinfo("Success", "Config generated!")

# --- Build Output ---
def build_output():
    template = template_text.get("1.0", tk.END)
    output = template

    for var, entry in sorted(entries.items(), key=lambda x: len(x[0]), reverse=True):
        value = entry.get()
        output = output.replace(f"${var}", value)

    return output

# --- Copy to Clipboard ---
def copy_to_clipboard():
    root.clipboard_clear()
    root.clipboard_append(preview_text.get("1.0", tk.END).strip())
    messagebox.showinfo("Copied", "Config copied to clipboard!")

# --- Live Preview ---
def update_preview(event=None):
    preview = build_output()
    preview_text.delete("1.0", tk.END)
    preview_text.insert(tk.END, preview)

# --- Load external template ---
def load_external():
    path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if path:
        with open(path, "r") as f:
            template_text.delete("1.0", tk.END)
            template_text.insert(tk.END, f.read())

        scan_variables()

# --- GUI ---
root = tk.Tk()
root.title("ConfigBench")
root.geometry("1100x650")

# Left panel
left_frame = tk.Frame(root)
left_frame.pack(side="left", fill="y", padx=10, pady=10)

# Template selection
tk.Label(left_frame, text="Template").pack(anchor="w")

template_var = tk.StringVar()
templates = get_templates()
template_dropdown = tk.OptionMenu(left_frame, template_var, *templates)
template_dropdown.pack(fill="x")

template_var.trace("w", load_template)
template_var.set(templates[0])

# Buttons
tk.Button(left_frame, text="Rescan Variables", command=scan_variables).pack(fill="x", pady=2)
tk.Button(left_frame, text="Load External Template", command=load_external).pack(fill="x", pady=2)
tk.Button(left_frame, text="Generate Config", command=generate_config).pack(fill="x", pady=10)

# Variables label
tk.Label(left_frame, text="Variables").pack(anchor="w")

# Scrollable variable panel
canvas = tk.Canvas(left_frame, height=400)
scrollbar = tk.Scrollbar(left_frame, orient="vertical", command=canvas.yview)
variable_frame = tk.Frame(canvas)

variable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=variable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"))
scrollbar.pack(side="right", fill="y")

# Center panel (template)
center_frame = tk.Frame(root)
center_frame.pack(side="left", fill="both", expand=True, padx=10)

tk.Label(center_frame, text="Template Editor").pack(anchor="w")

template_text = tk.Text(center_frame)
template_text.pack(fill="both", expand=True)

# Right panel (preview)
right_frame = tk.Frame(root)
right_frame.pack(side="right", fill="both", expand=True, padx=10)

tk.Label(right_frame, text="Live Preview").pack(anchor="w")

preview_text = tk.Text(right_frame, bg="#1e1e1e", fg="#00ff88")
preview_text.pack(fill="both", expand=True)

tk.Button(right_frame, text="Copy to Clipboard", command=copy_to_clipboard).pack(fill="x", pady=2)

root.mainloop()
