-- Seed stocking records (also created by SQLAlchemy create_all on startup)
CREATE TABLE IF NOT EXISTS seed_stocking (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  pond_id INTEGER NOT NULL REFERENCES ponds(pond_id) ON DELETE CASCADE,
  pl_stage VARCHAR(20) NOT NULL,
  supplier_name VARCHAR(120) NOT NULL,
  batch_number VARCHAR(100) NOT NULL,
  total_quantity INTEGER NOT NULL CHECK (total_quantity > 0),
  cost NUMERIC(12, 2) NOT NULL CHECK (cost > 0),
  stocking_date DATE NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  CONSTRAINT uq_seed_stocking_user_supplier_batch UNIQUE (user_id, supplier_name, batch_number)
);

CREATE INDEX IF NOT EXISTS ix_seed_stocking_user_id ON seed_stocking (user_id);
CREATE INDEX IF NOT EXISTS ix_seed_stocking_pond_id ON seed_stocking (pond_id);
CREATE INDEX IF NOT EXISTS ix_seed_stocking_stocking_date ON seed_stocking (stocking_date);
