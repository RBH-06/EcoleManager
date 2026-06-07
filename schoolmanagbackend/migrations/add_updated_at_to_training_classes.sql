-- Add updated_at column to training_classes table
ALTER TABLE training_classes ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
