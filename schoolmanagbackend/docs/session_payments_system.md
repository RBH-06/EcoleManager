# Session Payments System

## Overview

The Session Payments System allows you to track payment status for individual sessions per student, supporting both payment policies:
- **Per Session**: Each session has its own payment amount
- **Full Training**: Payment is calculated per session based on total training price

## Database Schema

### `session_payments` Table

```sql
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
```

## API Endpoints

### View Payment Status

#### Get Student Session Payments
```http
GET /api/session-payments/student/{studentId}
```
Returns all session payments for a specific student across all enrollments.

#### Get Enrollment Session Payments
```http
GET /api/session-payments/enrollment/{enrollmentId}
```
Returns all session payments for a specific enrollment with summary.

#### Get Session Payment Status
```http
GET /api/session-payments/session/{sessionId}
```
Returns payment status for all students in a specific session.

### Mark Payments

#### Mark Session as Paid
```http
POST /api/session-payments/enrollment/{enrollmentId}/session/{sessionId}/mark-paid
```
Body:
```json
{
  "payment_date": "2024-01-15",
  "payment_amount": 50.00,
  "payment_method": "cash",
  "transaction_reference": "CASH-001",
  "notes": "Payment received in cash"
}
```

#### Mark Session as Unpaid
```http
POST /api/session-payments/enrollment/{enrollmentId}/session/{sessionId}/mark-unpaid
```

#### Bulk Mark Sessions as Paid
```http
POST /api/session-payments/enrollment/{enrollmentId}/bulk-mark-paid
```
Body:
```json
{
  "sessionIds": ["session1", "session2", "session3"],
  "payment_data": {
    "payment_date": "2024-01-15",
    "payment_method": "bank_transfer",
    "transaction_reference": "BANK-001",
    "notes": "Bulk payment"
  }
}
```

### Reports

#### Get Payment Summary
```http
GET /api/session-payments/enrollment/{enrollmentId}/summary
```
Returns payment summary for an enrollment.

## Payment Policy Logic

### Per Session Policy
- Each session has its own payment amount (`price_per_session`)
- Students pay for each session individually
- Payment amount is taken from training's `price_per_session` field

### Full Training Policy
- Students pay for the entire training upfront
- Payment amount per session is calculated as: `price_full / total_sessions`
- All sessions can be marked as paid at once

## Usage Examples

### 1. Initialize Session Payments for New Enrollment
```javascript
const sessionPaymentService = require('./src/services/sessionPaymentService');

// When a student enrolls in a class
await sessionPaymentService.initializeSessionPayments(enrollmentId);
```

### 2. Mark Session as Paid
```javascript
const SessionPayment = require('./src/models/SessionPayment');

await SessionPayment.markSessionAsPaid(enrollmentId, sessionId, {
  payment_date: new Date().toISOString().split('T')[0],
  payment_amount: 50.00,
  payment_method: 'cash',
  transaction_reference: 'CASH-001',
  notes: 'Payment received'
});
```

### 3. Get Student Payment Report
```javascript
const sessionPaymentService = require('./src/services/sessionPaymentService');

const report = await sessionPaymentService.getStudentPaymentReport(studentId);
console.log(report);
```

## Features

### Automatic Amount Calculation
- If payment amount is not provided, it's automatically calculated based on training policy
- Per session: Uses `price_per_session`
- Full training: Calculates `price_full / total_sessions`

### Bulk Operations
- Mark multiple sessions as paid in one operation
- Useful for full training payments or bulk payments

### Comprehensive Reporting
- Payment status per student
- Payment status per enrollment
- Payment status per session
- Payment summaries with totals

### Audit Trail
- Tracks who marked payments (`marked_by`)
- Timestamps for creation and updates
- Transaction references for payment tracking

## Migration

To add this system to your existing database:

1. Run the migration:
```sql
-- Run the contents of migrations/create_session_payments_table.sql
```

2. Initialize payment records for existing enrollments:
```javascript
// For each existing enrollment, create payment records for all sessions
const enrollments = await Enrollment.findAll();
for (const enrollment of enrollments) {
  await sessionPaymentService.initializeSessionPayments(enrollment.id);
}
```

## Security

- All endpoints require authentication
- Permission check for `view_payments` is required
- Payment operations are logged with user information

## Error Handling

The system includes comprehensive error handling for:
- Invalid enrollment/session IDs
- Missing payment data
- Database constraint violations
- Permission errors

## Testing

Use the provided test script to verify the system:
```bash
node test_session_payments.js
```

This will show usage examples and can be modified to run actual tests with valid data. 