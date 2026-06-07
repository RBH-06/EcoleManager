-- Add unique constraint to prevent duplicate enrollments for the same student and class
ALTER TABLE enrollments ADD CONSTRAINT unique_student_class UNIQUE (student_id, class_id);
