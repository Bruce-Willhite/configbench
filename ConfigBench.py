import customtkinter as ctk
from tkinter import filedialog, messagebox
import re
import os

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

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
def load_template(filename):
    global current_template

    path = os.path.join(TEMPLATE_FOLDER, filename)

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            current_template = f.read()

        template_text.delete("1.0", "end")
        template_text.insert("end", current_template)

        scan_variables()
    else:
        messagebox.showwarning("Missing Template", f"Template file not found:\n{path}")

# --- Scan Variables ---
def scan_variables():
    global entries
    entries.clear()

    for widget in variable_frame.winfo_children():
        widget.destroy()

    template = template_text.get("1.0", "end")

    vars_found = sorted(set(re.findall(r"\$([a-zA-Z0-9_-]+)", template)))

    if not vars_found:
        ctk.CTkLabel(variable_frame, text="No variables found").pack()
        return

    for var in vars_found:
        row = ctk.CTkFrame(variable_frame)
        row.pack(fill="x", pady=2)

        label = ctk.CTkLabel(row, text=var, width=140, anchor="w")
        label.pack(side="left", padx=4)

        entry = ctk.CTkEntry(row)
        entry.pack(side="left", fill="x", expand=True, padx=4)
        entry.bind("<KeyRelease>", update_preview)

        entries[var] = entry

# --- Generate Output ---
def generate_config():
    output = build_output()

    path = filedialog.asksaveasfilename(defaultextension=".txt")
    if path:
        with open(path, "w", encoding="utf-8") as f:
            f.write(output)

        messagebox.showinfo("Success", "Config generated!")

# --- Build Output ---
def build_output():
    output = template_text.get("1.0", "end").rstrip("\n")

    for var, entry in entries.items():
        value = entry.get()
        output = re.sub(r'\$' + re.escape(var) + r'(?![a-zA-Z0-9_-])', value, output)

    return output

# --- Copy to Clipboard ---
def copy_to_clipboard():
    root.clipboard_clear()
    root.clipboard_append(build_output())
    messagebox.showinfo("Copied", "Config copied to clipboard!")

# --- Live Preview ---
def update_preview(event=None):
    preview = build_output()
    preview_text.delete("1.0", "end")
    preview_text.insert("end", preview)

# --- Load external template ---
def load_external():
    path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if path:
        with open(path, "r", encoding="utf-8") as f:
            template_text.delete("1.0", "end")
            template_text.insert("end", f.read())

        scan_variables()

# --- GUI ---
root = ctk.CTk()
root.title("ConfigBench")
root.geometry("1100x650")
root.minsize(600, 400)
root.resizable(True, True)

# Left panel
left_frame = ctk.CTkFrame(root, width=320)
left_frame.pack(side="left", fill="y", padx=10, pady=10)
left_frame.pack_propagate(False)

ctk.CTkLabel(left_frame, text="Template", anchor="w").pack(fill="x", padx=8, pady=(8, 2))

templates = get_templates()
template_dropdown = ctk.CTkOptionMenu(left_frame, values=templates, command=load_template)
template_dropdown.pack(fill="x", padx=8, pady=(2, 8))

for btn_text, btn_cmd in [
    ("Rescan Variables", scan_variables),
    ("Load External Template", load_external),
    ("Generate Config", generate_config),
]:
    ctk.CTkButton(left_frame, text=btn_text, command=btn_cmd, height=38).pack(fill="x", padx=10, pady=4)

ctk.CTkLabel(left_frame, text="Variables", anchor="w").pack(fill="x", padx=8, pady=(10, 2))

variable_frame = ctk.CTkScrollableFrame(left_frame)
variable_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

# Tabbed center area
tab_view = ctk.CTkTabview(root)
tab_view.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=10)

tab_view.add("Template Editor")
tab_view.add("Live Preview")

template_text = ctk.CTkTextbox(tab_view.tab("Template Editor"))
template_text.pack(fill="both", expand=True, padx=8, pady=(0, 8))

preview_text = ctk.CTkTextbox(tab_view.tab("Live Preview"), text_color="#00ff88")
preview_text.pack(fill="both", expand=True, padx=8, pady=(0, 4))

ctk.CTkButton(tab_view.tab("Live Preview"), text="Copy to Clipboard", command=copy_to_clipboard).pack(fill="x", padx=8, pady=(0, 8))

# Auto-load first template
template_dropdown.set(templates[0])
if templates[0] != "No Templates Found":
    load_template(templates[0])

root.mainloop()
