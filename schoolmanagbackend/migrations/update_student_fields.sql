-- Remove unwanted fields from students table
ALTER TABLE students 
  DROP COLUMN IF EXISTS address,
  DROP COLUMN IF EXISTS emergency_contact_name,
  DROP COLUMN IF EXISTS emergency_contact_phone,
  DROP COLUMN IF EXISTS emergency_contact_relationship,
  DROP COLUMN IF EXISTS parent_guardian_email,
  DROP COLUMN IF EXISTS medical_notes,
  DROP COLUMN IF EXISTS status,
  DROP COLUMN IF EXISTS created_by,
  DROP COLUMN IF EXISTS created_at,
  DROP COLUMN IF EXISTS updated_at;

-- Add/rename fields if needed

ALTER TABLE students RENAME COLUMN date_of_birth TO bday;
ALTER TABLE students RENAME COLUMN parent_guardian_name TO parentname;
ALTER TABLE students RENAME COLUMN parent_guardian_phone TO parentphone;

-- Add registration_date and notes if not present
ALTER TABLE students 
  ADD COLUMN IF NOT EXISTS registration_date DATE DEFAULT CURRENT_DATE,
  ADD COLUMN IF NOT EXISTS notes TEXT;
