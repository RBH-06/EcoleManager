-- Add payment_style column to enrollments table
ALTER TABLE enrollments ADD COLUMN payment_style VARCHAR(20) DEFAULT 'per_training';
