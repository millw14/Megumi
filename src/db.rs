/// db.rs — Megumi's Memories (SQLite persistence)
///
/// She never forgets. Everything is stored locally, forever.

use rusqlite::{Connection, params};
use std::path::Path;

use crate::state::MegumiState;

/// Initialize the database, creating the state table if needed
pub fn init_db(db_path: &Path) -> Result<Connection, Box<dyn std::error::Error>> {
    let conn = Connection::open(db_path)?;
    conn.execute(
        "CREATE TABLE IF NOT EXISTS state (id INTEGER PRIMARY KEY, data TEXT NOT NULL)",
        [],
    )?;
    Ok(conn)
}

/// Load state from DB, or return None if no state exists yet
pub fn load_state(conn: &Connection) -> Result<Option<MegumiState>, Box<dyn std::error::Error>> {
    let result = conn.query_row(
        "SELECT data FROM state WHERE id = 1",
        [],
        |row| row.get::<_, String>(0),
    );

    match result {
        Ok(json_str) => {
            let state: MegumiState = serde_json::from_str(&json_str)?;
            Ok(Some(state))
        }
        Err(rusqlite::Error::QueryReturnedNoRows) => Ok(None),
        Err(e) => Err(e.into()),
    }
}

/// Save state to DB (insert or update)
pub fn save_state(conn: &Connection, state: &MegumiState) -> Result<(), Box<dyn std::error::Error>> {
    let json = serde_json::to_string(state)?;
    conn.execute(
        "INSERT INTO state (id, data) VALUES (1, ?1)
         ON CONFLICT(id) DO UPDATE SET data = excluded.data",
        params![json],
    )?;
    Ok(())
}
