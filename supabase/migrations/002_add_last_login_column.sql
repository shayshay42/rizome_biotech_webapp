-- Add last_login column to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login TIMESTAMP;

-- Add comment
COMMENT ON COLUMN users.last_login IS 'Last login timestamp for user activity tracking';