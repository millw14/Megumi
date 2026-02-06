"""Quick script to check database contents"""
import sqlite3

db_path = 'data/megumi_memories.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print('=== TABLES ===')
for t in tables:
    print(f'  - {t[0]}')

print()

# Count rows in each table
for t in tables:
    cursor.execute(f'SELECT COUNT(*) FROM {t[0]}')
    count = cursor.fetchone()[0]
    print(f'{t[0]}: {count} rows')

print()

# Show sample observations
print('=== RECENT OBSERVATIONS (last 5) ===')
cursor.execute('SELECT id, timestamp, observation_type, window_title FROM observations ORDER BY id DESC LIMIT 5')
for row in cursor.fetchall():
    title = (row[3][:50] + '...') if row[3] and len(row[3]) > 50 else (row[3] or 'N/A')
    ts = row[1][:19] if row[1] else 'N/A'
    print(f'  [{row[0]}] {ts} | {row[2]} | {title}')

print()

# Show sample actions (state-action pairs)
print('=== RECENT STATE-ACTION PAIRS (last 5) ===')
cursor.execute('SELECT id, timestamp, action_type, target_element, value FROM actions ORDER BY id DESC LIMIT 5')
for row in cursor.fetchall():
    ts = row[1][:19] if row[1] else 'N/A'
    target = (row[3][:40] + '...') if row[3] and len(row[3]) > 40 else (row[3] or 'N/A')
    value = (row[4][:30] + '...') if row[4] and len(row[4]) > 30 else (row[4] or '-')
    print(f'  [{row[0]}] {ts} | {row[2]} | {target} | keys: {value}')

print()

# Show patterns
print('=== LEARNED PATTERNS ===')
cursor.execute('SELECT id, pattern_type, pattern_name, frequency, confidence FROM patterns ORDER BY frequency DESC LIMIT 10')
patterns = cursor.fetchall()
if patterns:
    for row in patterns:
        print(f'  [{row[0]}] {row[1]} | {row[2]} | freq:{row[3]} conf:{row[4]:.2f}')
else:
    print('  (none yet - need more observations)')

print()

# Sessions
print('=== SESSIONS ===')
cursor.execute('SELECT id, started_at, ended_at, summary FROM sessions ORDER BY id DESC LIMIT 3')
for row in cursor.fetchall():
    ended = row[2][:19] if row[2] else 'ongoing'
    print(f'  [{row[0]}] Started: {row[1][:19]} | Ended: {ended}')

conn.close()
