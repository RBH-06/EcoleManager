-- Add paymentpolicy enum type and column, remove payment_type from trainings
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'paymentpolicy_enum') THEN
        CREATE TYPE paymentpolicy_enum AS ENUM ('per session', 'at once');
    END IF;
END$$;

ALTER TABLE trainings DROP COLUMN IF EXISTS payment_type;
ALTER TABLE trainings ADD COLUMN paymentpolicy paymentpolicy_enum DEFAULT 'per session';
