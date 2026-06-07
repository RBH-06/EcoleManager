-- Create session_payments table to track payment status for individual sessions
CREATE TABLE session_payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    enrollment_id UUID REFERENCES enrollments(id) ON DELETE CASCADE,
    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
    is_paid BOOLEAN DEFAULT FALSE,
    payment_date DATE,
    payment_amount DECIMAL(10,2),
    payment_method payment_method_enum,
    transaction_reference VARCHAR(100),
    notes TEXT,
    marked_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(enrollment_id, session_id)
);

-- Add indexes for better performance
CREATE INDEX idx_session_payments_enrollment_id ON session_payments(enrollment_id);
CREATE INDEX idx_session_payments_session_id ON session_payments(session_id);
CREATE INDEX idx_session_payments_is_paid ON session_payments(is_paid);
CREATE INDEX idx_session_payments_payment_date ON session_payments(payment_date);

-- Add trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_session_payments_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_session_payments_updated_at
    BEFORE UPDATE ON session_payments
    FOR EACH ROW
    EXECUTE FUNCTION update_session_payments_updated_at(); 