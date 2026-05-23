# ConfigBench

A GUI application for generating network device configs from templates.

**Requirements:** Python 3 with tkinter (included in the standard library)

**Run:**
```bash
python ConfigBench.py
```

## How it works

1. On startup the first available template loads automatically
2. Fill in the variable fields — any `$variable` in the template gets a form field
3. The **Live Preview** panel updates in real time as you type
4. Click **Copy to Clipboard** to copy the config directly, or **Generate Config** to save it to a file
5. Use **Load External Template** to open any `.txt` file outside the templates folder

## Variable syntax

Use `$variable_name` in your templates. Variable names support letters, numbers, underscores, and dashes. Overlapping names (e.g. `$host` and `$hostname`) are handled correctly — longer names are always substituted first.

```
hostname $hostname
ip address $ip_address $subnet_mask
```

## Adding templates

Drop any `.txt` file into the `templates/` folder and it will appear in the dropdown. Use **Rescan Variables** to refresh the field list after editing a template.
