-- Add total_price column to trainings if not exists
ALTER TABLE trainings ADD COLUMN IF NOT EXISTS total_price DECIMAL(10,2);
