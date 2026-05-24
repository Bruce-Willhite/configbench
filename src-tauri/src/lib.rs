use std::fs;
use std::path::PathBuf;
use tauri_plugin_dialog::FilePath;

// ── Embedded templates (baked into the binary at compile time) ──
const EMBEDDED: &[(&str, &str)] = &[
    ("router.txt", include_str!("../../templates/router.txt")),
];

fn embedded_content(name: &str) -> Option<&'static str> {
    EMBEDDED.iter().find(|(n, _)| *n == name).map(|(_, c)| *c)
}

// Optional on-disk folder for user-added templates (not required)
fn template_dir() -> PathBuf {
    if cfg!(debug_assertions) {
        PathBuf::from(env!("CARGO_MANIFEST_DIR"))
            .join("..")
            .join("templates")
    } else {
        std::env::current_exe()
            .unwrap()
            .parent()
            .unwrap()
            .join("templates")
    }
}

#[tauri::command]
fn get_templates() -> Vec<String> {
    // Start with the embedded templates
    let mut names: Vec<String> = EMBEDDED.iter().map(|(n, _)| n.to_string()).collect();

    // Merge in any .txt files from the on-disk folder (user additions)
    let dir = template_dir();
    if dir.exists() {
        if let Ok(entries) = fs::read_dir(&dir) {
            for entry in entries.filter_map(|e| e.ok()) {
                if entry.path().extension().map(|x| x == "txt").unwrap_or(false) {
                    if let Ok(fname) = entry.file_name().into_string() {
                        if !names.contains(&fname) {
                            names.push(fname);
                        }
                    }
                }
            }
        }
    }

    names.sort();
    names
}

#[tauri::command]
fn load_template(name: String) -> Result<String, String> {
    // Prefer on-disk version (allows user to override embedded templates)
    let path = template_dir().join(&name);
    if path.exists() {
        return fs::read_to_string(&path).map_err(|e| e.to_string());
    }
    // Fall back to embedded
    embedded_content(&name)
        .map(|s| s.to_string())
        .ok_or_else(|| format!("Template '{}' not found", name))
}

#[tauri::command]
fn load_external_dialog(app: tauri::AppHandle) -> Result<Option<serde_json::Value>, String> {
    use tauri_plugin_dialog::DialogExt;

    let result = app
        .dialog()
        .file()
        .add_filter("Text Files", &["txt"])
        .blocking_pick_file();

    match result {
        Some(file_path) => {
            let path = match file_path {
                FilePath::Path(p) => p,
                _ => return Err("Unsupported path type".to_string()),
            };
            let content = fs::read_to_string(&path).map_err(|e| e.to_string())?;
            let filename = path
                .file_name()
                .and_then(|n| n.to_str())
                .unwrap_or("external")
                .to_string();
            Ok(Some(serde_json::json!({ "filename": filename, "content": content })))
        }
        None => Ok(None),
    }
}

#[tauri::command]
fn save_config_dialog(app: tauri::AppHandle, content: String) -> Result<bool, String> {
    use tauri_plugin_dialog::DialogExt;

    let result = app
        .dialog()
        .file()
        .add_filter("Text Files", &["txt"])
        .set_file_name("config.txt")
        .blocking_save_file();

    match result {
        Some(file_path) => {
            let path = match file_path {
                FilePath::Path(p) => p,
                _ => return Err("Unsupported path type".to_string()),
            };
            fs::write(&path, content).map_err(|e| e.to_string())?;
            Ok(true)
        }
        None => Ok(false),
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .invoke_handler(tauri::generate_handler![
            get_templates,
            load_template,
            load_external_dialog,
            save_config_dialog,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
