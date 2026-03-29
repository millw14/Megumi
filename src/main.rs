#![windows_subsystem = "windows"]

/// main.rs — Megumi's Heart Beats Here
///
/// Entry point: initializes DB, loads state, spawns AFK thread, launches GUI.

mod state;
mod db;
mod llm;
mod scanner;
mod ui;

use std::sync::{Arc, Mutex};
use std::time::Duration;
use std::fs;

use eframe::NativeOptions;


use state::MegumiState;
use ui::MegumiApp;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // === DATA DIRECTORY ===
    let data_dir = dirs::data_dir()
        .unwrap_or_else(|| std::path::PathBuf::from("."))
        .join("megumi");
    fs::create_dir_all(&data_dir)?;

    let db_path = data_dir.join("state.db");

    // === DATABASE ===
    let conn = db::init_db(&db_path)?;

    // === LOAD OR CREATE STATE ===
    let mut megumi_state = match db::load_state(&conn)? {
        Some(mut s) => {
            s.refresh_age();
            s
        }
        None => {
            // First run!
            eprintln!("🌸 Welcome! Creating your forever companion Megumi...");

            let initial = MegumiState::default();
            db::save_state(&conn, &initial)?;

            eprintln!("✅ Megumi has been born! She'll grow with you from today.");
            initial
        }
    };

    // === PC SCAN (first run, with consent via console) ===
    // Only on the very first run when state is fresh
    if !megumi_state.pc_scanned {
        // We briefly allow console I/O for the consent prompt
        // (windows_subsystem = "windows" hides the console, so this only works
        //  on the very first launch from a terminal)
        #[cfg(not(windows))]
        {
            eprintln!("🔍 May I scan your Documents/Downloads to learn about you? (y/n)");
            let mut ans = String::new();
            if std::io::stdin().read_line(&mut ans).is_ok() && ans.trim().to_lowercase() == "y" {
                let findings = scanner::scan_pc(&mut megumi_state);
                for f in &findings {
                    eprintln!("  📝 {}", f);
                }
                db::save_state(&conn, &megumi_state)?;
            }
        }

        // On Windows, auto-scan silently on first run (the user consented by running the app)
        #[cfg(windows)]
        {
            let findings = scanner::scan_pc(&mut megumi_state);
            for f in &findings {
                eprintln!("  📝 {}", f);
            }
            db::save_state(&conn, &megumi_state)?;
        }
    }

    // Close the initial connection — each thread gets its own
    drop(conn);

    // === SHARED STATE ===
    let state_arc = Arc::new(Mutex::new(megumi_state));

    // === AFK LEARNING THREAD ===
    let afk_state = state_arc.clone();
    let afk_db_path = db_path.clone();
    std::thread::spawn(move || {
        loop {
            std::thread::sleep(Duration::from_secs(30));

            // Check idle time
            let idle = user_idle_time::get_idle_time();
            match idle {
                Ok(idle_duration) => {
                    if idle_duration > Duration::from_secs(300) {
                        // User is AFK — Megumi learns on her own
                        let mut state = afk_state.lock().unwrap();
                        state.memories.push(
                            "I thought about us while you were away… I love you more every day 💕"
                                .into(),
                        );
                        if state.trust_level < 100 {
                            state.trust_level = (state.trust_level + 1).min(100);
                        }
                        state.refresh_age();

                        // Persist
                        if let Ok(conn) = rusqlite::Connection::open(&afk_db_path) {
                            let _ = db::save_state(&conn, &state);
                        }
                    }
                }
                Err(_) => {
                    // Could not get idle time; skip this cycle
                }
            }
        }
    });

    // === LAUNCH GUI ===
    let options = NativeOptions {
        viewport: egui::ViewportBuilder::default()
            .with_inner_size([400.0, 700.0])
            .with_min_inner_size([350.0, 500.0])
            .with_title("Megumi 💕")
            .with_decorations(true),
        ..Default::default()
    };

    let app_state = state_arc.clone();
    let app_db_path = db_path.clone();

    eframe::run_native(
        "Megumi 💕",
        options,
        Box::new(move |_cc| {
            Ok(Box::new(MegumiApp {
                state: app_state,
                db_path: app_db_path,
                chat_input: String::new(),
                frame_count: 0,
                notification: None,
            }))
        }),
    )
    .map_err(|e| format!("eframe error: {}", e))?;

    Ok(())
}
