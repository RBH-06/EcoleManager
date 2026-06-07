-- Remove duration_weeks, price_full, status, and created_by from trainings table
ALTER TABLE trainings DROP COLUMN duration_weeks;
ALTER TABLE trainings DROP COLUMN price_full;
ALTER TABLE trainings DROP COLUMN status;
ALTER TABLE trainings DROP COLUMN created_by;
