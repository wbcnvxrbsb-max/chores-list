-- Children in the household
CREATE TABLE IF NOT EXISTS children (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Chore templates (recurring chores assigned to each child)
-- frequency: 'daily', 'weekly', 'monthly', 'oneoff'
CREATE TABLE IF NOT EXISTS chores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    child_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    frequency TEXT DEFAULT 'daily',
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (child_id) REFERENCES children(id) ON DELETE CASCADE
);

-- Completion records (one row per chore per period when completed)
-- For daily/oneoff: date is the day
-- For weekly: date is any day within that week
-- For monthly: date is any day within that month
CREATE TABLE IF NOT EXISTS chore_completions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chore_id INTEGER NOT NULL,
    date DATE NOT NULL,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chore_id) REFERENCES chores(id) ON DELETE CASCADE,
    UNIQUE(chore_id, date)
);

-- App settings (stores parent PIN hash, etc.)
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

-- Indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_completions_date ON chore_completions(date);
CREATE INDEX IF NOT EXISTS idx_completions_chore ON chore_completions(chore_id);
CREATE INDEX IF NOT EXISTS idx_chores_child ON chores(child_id);
