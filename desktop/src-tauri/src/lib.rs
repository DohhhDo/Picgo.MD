// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/
use tauri_plugin_shell::ShellExt;
use tauri::{Manager, Emitter};

#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

#[tauri::command]
fn save_md_file(path: String, content: String) -> Result<(), String> {
    std::fs::write(&path, content).map_err(|e| e.to_string())
}

#[tauri::command]
async fn http_get(url: String) -> Result<String, String> {
    println!("Rust HTTP GET request to: {}", url);
    
    let client = reqwest::Client::new();
    match client.get(&url).send().await {
        Ok(response) => {
            println!("Response status: {}", response.status());
            match response.text().await {
                Ok(text) => {
                    println!("Response body: {}", text);
                    Ok(text)
                }
                Err(e) => Err(format!("Failed to read response body: {}", e))
            }
        }
        Err(e) => {
            println!("Request failed: {}", e);
            Err(format!("HTTP request failed: {}", e))
        }
    }
}

#[tauri::command]
async fn http_post(url: String, body: String) -> Result<String, String> {
    println!("Rust HTTP POST request to: {}", url);
    
    let client = reqwest::Client::new();
    match client.post(&url)
        .header("Content-Type", "application/json")
        .body(body)
        .send().await {
        Ok(response) => {
            println!("Response status: {}", response.status());
            match response.text().await {
                Ok(text) => {
                    println!("Response body: {}", text);
                    Ok(text)
                }
                Err(e) => Err(format!("Failed to read response body: {}", e))
            }
        }
        Err(e) => {
            println!("Request failed: {}", e);
            Err(format!("HTTP request failed: {}", e))
        }
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_shell::init())
        .setup(|app| {
            // 启动后端 sidecar
            let _child = app
                .shell()
                .sidecar("meowdown-backend")
                .expect("create sidecar")
                .spawn()
                .expect("spawn sidecar");
            // 简单延迟后，在主窗口里注入一个事件，前端拿到后可主动重试连接
            if app.get_webview_window("main").is_some() {
                let app_handle = app.app_handle().clone();
                std::thread::spawn(move || {
                    std::thread::sleep(std::time::Duration::from_millis(500));
                    let _ = app_handle.emit("backend_started", ());
                });
            }
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![greet, save_md_file, http_get, http_post])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
