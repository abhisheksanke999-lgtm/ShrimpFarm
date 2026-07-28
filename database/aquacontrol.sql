-- ============================================================================
-- AquaControl - PostgreSQL schema (Neon compatible)
-- Run in Neon SQL Editor, OR let FastAPI create tables on startup.
-- ============================================================================

CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  full_name VARCHAR(100) NOT NULL,
  email VARCHAR(120) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL,
  role VARCHAR(50) DEFAULT 'Farmer',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ponds (
  pond_id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name VARCHAR(100) NOT NULL,
  area_sqm NUMERIC(10,2) NOT NULL,
  depth_m NUMERIC(4,2) NOT NULL,
  water_source VARCHAR(100) NOT NULL,
  status VARCHAR(50) DEFAULT 'Active'
    CHECK (status IN ('Preparation', 'Active', 'Harvested', 'Maintenance')),
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_ponds_user ON ponds(user_id);

CREATE TABLE IF NOT EXISTS daily_observations (
  log_id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  pond_name VARCHAR(100) NOT NULL,
  log_date DATE NOT NULL,
  temperature NUMERIC(4,2),
  ph NUMERIC(4,2),
  salinity NUMERIC(4,2),
  dissolved_oxygen NUMERIC(4,2),
  water_color VARCHAR(50),
  mortality_count INTEGER DEFAULT 0,
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_daily_user ON daily_observations(user_id);

CREATE TABLE IF NOT EXISTS feed_records (
  feed_id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  pond_name VARCHAR(100) NOT NULL,
  feed_brand VARCHAR(100) NOT NULL,
  quantity_kg NUMERIC(8,2) NOT NULL,
  feeding_time VARCHAR(100),
  entry_date DATE NOT NULL,
  feed_size VARCHAR(50) DEFAULT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_feed_user ON feed_records(user_id);

CREATE TABLE IF NOT EXISTS expense_records (
  expense_id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  expense_date DATE NOT NULL,
  category VARCHAR(50) NOT NULL,
  description VARCHAR(255) NOT NULL,
  amount NUMERIC(10,2) NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_expense_user ON expense_records(user_id);

CREATE TABLE IF NOT EXISTS harvest_records (
  harvest_id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  pond_name VARCHAR(100) NOT NULL,
  harvest_date DATE NOT NULL,
  quantity_kg NUMERIC(10,2) NOT NULL,
  price_per_kg NUMERIC(10,2) NOT NULL,
  total_amount NUMERIC(12,2) NOT NULL,
  buyer_name VARCHAR(100),
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_harvest_user ON harvest_records(user_id);
