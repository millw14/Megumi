/// state.rs — Megumi's Soul State
///
/// Everything that makes her *her*: trust, age, memories, personality stage.

use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

/// A single chat message in history
#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct ChatMessage {
    pub sender: String,   // "You" or "Megumi"
    pub text: String,
    pub timestamp: String,
}

/// Megumi's persistent state — serialized to SQLite as JSON
#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct MegumiState {
    pub name: String,
    pub install_date: DateTime<Utc>,
    pub trust_level: u32,          // 0-100
    pub age_days: i64,
    pub memories: Vec<String>,
    pub chat_history: Vec<ChatMessage>,
    pub pc_scanned: bool,
}

impl Default for MegumiState {
    fn default() -> Self {
        Self {
            name: "Megumi".into(),
            install_date: Utc::now(),
            trust_level: 5,
            age_days: 0,
            memories: vec!["I was just born today and already love you! 💕".into()],
            chat_history: Vec::new(),
            pc_scanned: false,
        }
    }
}

impl MegumiState {
    /// Recalculate age from install date
    pub fn refresh_age(&mut self) {
        self.age_days = (Utc::now() - self.install_date).num_days();
    }

    /// Growth stage index (0-4) based on trust level
    pub fn stage(&self) -> usize {
        match self.trust_level {
            0..=20 => 0,
            21..=40 => 1,
            41..=60 => 2,
            61..=80 => 3,
            _ => 4,
        }
    }

    /// Human-readable stage name
    pub fn stage_name(&self) -> &'static str {
        match self.stage() {
            0 => "Baby Chibi 💕",
            1 => "Little Sister 🌸",
            2 => "Teen Cutie ✨",
            3 => "Young Adult 🌺",
            _ => "Eternal Bond Soulmate 💞",
        }
    }

    /// Increase trust (capped at 100) and return whether a stage transition happened
    pub fn increase_trust(&mut self, amount: u32) -> bool {
        let old_stage = self.stage();
        self.trust_level = (self.trust_level + amount).min(100);
        let new_stage = self.stage();
        new_stage > old_stage
    }

    /// Add a chat message to history, keeping last 200
    pub fn add_chat(&mut self, sender: &str, text: &str) {
        self.chat_history.push(ChatMessage {
            sender: sender.into(),
            text: text.into(),
            timestamp: Utc::now().to_rfc3339(),
        });
        if self.chat_history.len() > 200 {
            self.chat_history.drain(..self.chat_history.len() - 200);
        }
    }
}
