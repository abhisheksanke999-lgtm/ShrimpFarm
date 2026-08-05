-- Optional: pending signup rows for email OTP (also created by SQLAlchemy create_all)
CREATE TABLE IF NOT EXISTS pending_registrations (
  id SERIAL PRIMARY KEY,
  full_name VARCHAR(100) NOT NULL,
  email VARCHAR(120) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL,
  otp_code VARCHAR(12) NOT NULL,
  otp_expiry TIMESTAMPTZ NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_pending_registrations_email ON pending_registrations (email);
