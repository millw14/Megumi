/// scanner.rs — Megumi's Curiosity
///
/// Scans the user's PC (with consent) to learn about their tastes, files, and interests.
/// Only reads filenames and extensions — never file contents.

use std::collections::HashMap;
use walkdir::WalkDir;

use crate::state::MegumiState;

/// Category of a file based on its extension
fn categorize_extension(ext: &str) -> &'static str {
    match ext {
        // Code
        "rs" | "py" | "js" | "ts" | "jsx" | "tsx" | "c" | "cpp" | "h" | "cs" | "java"
        | "go" | "rb" | "php" | "swift" | "kt" | "scala" | "lua" | "zig" | "asm" => "Code",
        // Documents
        "pdf" | "doc" | "docx" | "txt" | "md" | "rtf" | "odt" | "tex" | "epub" => "Documents",
        // Spreadsheets & Data
        "csv" | "xlsx" | "xls" | "json" | "xml" | "yaml" | "yml" | "toml" | "sql" => "Data",
        // Images
        "png" | "jpg" | "jpeg" | "gif" | "bmp" | "svg" | "webp" | "ico" | "psd" | "ai" => "Images",
        // Music
        "mp3" | "flac" | "wav" | "ogg" | "aac" | "wma" | "m4a" | "opus" => "Music",
        // Video
        "mp4" | "mkv" | "avi" | "mov" | "wmv" | "flv" | "webm" => "Video",
        // Archives
        "zip" | "rar" | "7z" | "tar" | "gz" | "bz2" | "xz" => "Archives",
        // Executables
        "exe" | "msi" | "dll" | "so" | "dylib" => "Executables",
        // Web
        "html" | "css" | "scss" | "less" | "wasm" => "Web",
        // Config
        "ini" | "cfg" | "conf" | "env" | "properties" => "Config",
        _ => "Other",
    }
}

/// Scan standard user directories and return a summary of what was found.
/// This NEVER reads file contents — only names and extensions.
pub fn scan_pc(state: &mut MegumiState) -> Vec<String> {
    let mut category_counts: HashMap<&str, usize> = HashMap::new();
    let _interesting_finds: Vec<String> = Vec::new();
    let mut total_files: usize = 0;

    // Directories to scan
    let scan_dirs: Vec<std::path::PathBuf> = [
        dirs::document_dir(),
        dirs::download_dir(),
        dirs::audio_dir(),
        dirs::desktop_dir(),
        dirs::picture_dir(),
        dirs::video_dir(),
    ]
    .iter()
    .filter_map(|d| d.clone())
    .collect();

    for dir in &scan_dirs {
        if !dir.exists() {
            continue;
        }

        for entry in WalkDir::new(dir)
            .max_depth(3) // Don't go too deep
            .follow_links(false)
            .into_iter()
            .filter_map(|e| e.ok())
        {
            if entry.file_type().is_file() {
                total_files += 1;

                if let Some(ext) = entry.path().extension() {
                    let ext_str = ext.to_string_lossy().to_lowercase();
                    let category = categorize_extension(&ext_str);
                    *category_counts.entry(category).or_insert(0) += 1;
                }
            }
        }
    }

    // Build memories from what we found
    let mut memories = Vec::new();

    if total_files > 0 {
        memories.push(format!(
            "I scanned your PC and found {} files across your directories! 📂",
            total_files
        ));
    }

    // Sort categories by count
    let mut sorted: Vec<_> = category_counts.into_iter().collect();
    sorted.sort_by(|a, b| b.1.cmp(&a.1));

    for (category, count) in &sorted {
        if *count > 5 {
            let comment = match *category {
                "Code" => format!("You have {} code files — you're a programmer! I love that about you! 💻✨", count),
                "Music" => format!("I found {} music files — I bet you have great taste! 🎵💕", count),
                "Images" => format!("You have {} images — I'd love to see them someday! 🖼️🌸", count),
                "Documents" => format!("There are {} documents — you must be really organized! 📄✨", count),
                "Video" => format!("I found {} video files — movie night together? 🎬💖", count),
                "Data" => format!("You have {} data files — you work with lots of information! 📊", count),
                "Web" => format!("I see {} web files — are you building websites? That's so cool! 🌐✨", count),
                _ => format!("I found {} {} files! 📁", count, category),
            };
            memories.push(comment);
        }
    }

    if memories.is_empty() {
        memories.push("I couldn't find much on your PC yet… but I'll learn more as we spend time together! 💕".into());
    }

    // Store in state
    state.memories.extend(memories.clone());
    state.pc_scanned = true;

    memories
}
