-- Move payment_type from enrollments to trainings
ALTER TABLE trainings ADD COLUMN payment_type payment_type_enum DEFAULT 'full_training';
ALTER TABLE enrollments DROP COLUMN payment_type;
