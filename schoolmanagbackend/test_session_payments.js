const axios = require('axios');

// Configuration
const BASE_URL = 'http://localhost:3000/api';
const AUTH_TOKEN = 'your_auth_token_here'; // Replace with actual token

const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Authorization': `Bearer ${AUTH_TOKEN}`,
    'Content-Type': 'application/json'
  }
});

// Test functions
async function testSessionPayments() {
  try {
    console.log('=== Testing Session Payments System ===\n');

    // 1. Get payment status for a student
    console.log('1. Getting payment status for student...');
    const studentId = 'student-uuid-here';
    const studentPayments = await api.get(`/session-payments/student/${studentId}`);
    console.log('Student payments:', studentPayments.data);

    // 2. Get payment status for an enrollment
    console.log('\n2. Getting payment status for enrollment...');
    const enrollmentId = 'enrollment-uuid-here';
    const enrollmentPayments = await api.get(`/session-payments/enrollment/${enrollmentId}`);
    console.log('Enrollment payments:', enrollmentPayments.data);

    // 3. Get payment status for a session
    console.log('\n3. Getting payment status for session...');
    const sessionId = 'session-uuid-here';
    const sessionPayments = await api.get(`/session-payments/session/${sessionId}`);
    console.log('Session payments:', sessionPayments.data);

    // 4. Mark a session as paid
    console.log('\n4. Marking session as paid...');
    const markPaidResponse = await api.post(`/session-payments/enrollment/${enrollmentId}/session/${sessionId}/mark-paid`, {
      payment_date: new Date().toISOString().split('T')[0],
      payment_amount: 50.00,
      payment_method: 'cash',
      transaction_reference: 'CASH-001',
      notes: 'Payment received in cash'
    });
    console.log('Mark paid response:', markPaidResponse.data);

    // 5. Bulk mark multiple sessions as paid
    console.log('\n5. Bulk marking sessions as paid...');
    const sessionIds = ['session-1-uuid', 'session-2-uuid', 'session-3-uuid'];
    const bulkMarkResponse = await api.post(`/session-payments/enrollment/${enrollmentId}/bulk-mark-paid`, {
      sessionIds: sessionIds,
      payment_data: {
        payment_date: new Date().toISOString().split('T')[0],
        payment_method: 'bank_transfer',
        transaction_reference: 'BANK-001',
        notes: 'Bulk payment via bank transfer'
      }
    });
    console.log('Bulk mark response:', bulkMarkResponse.data);

    // 6. Get payment summary
    console.log('\n6. Getting payment summary...');
    const summaryResponse = await api.get(`/session-payments/enrollment/${enrollmentId}/summary`);
    console.log('Payment summary:', summaryResponse.data);

    console.log('\n=== All tests completed successfully! ===');

  } catch (error) {
    console.error('Error testing session payments:', error.response?.data || error.message);
  }
}

// Example usage scenarios
function showUsageExamples() {
  console.log(`
=== Session Payments System Usage Examples ===

1. VIEW PAYMENT STATUS:
   - Get all session payments for a student:
     GET /api/session-payments/student/{studentId}
   
   - Get all session payments for an enrollment:
     GET /api/session-payments/enrollment/{enrollmentId}
   
   - Get payment status for all students in a session:
     GET /api/session-payments/session/{sessionId}

2. MARK PAYMENTS:
   - Mark a single session as paid:
     POST /api/session-payments/enrollment/{enrollmentId}/session/{sessionId}/mark-paid
     Body: {
       "payment_date": "2024-01-15",
       "payment_amount": 50.00,
       "payment_method": "cash",
       "transaction_reference": "CASH-001",
       "notes": "Payment received"
     }
   
   - Mark multiple sessions as paid:
     POST /api/session-payments/enrollment/{enrollmentId}/bulk-mark-paid
     Body: {
       "sessionIds": ["session1", "session2", "session3"],
       "payment_data": {
         "payment_date": "2024-01-15",
         "payment_method": "bank_transfer",
         "transaction_reference": "BANK-001"
       }
     }
   
   - Mark a session as unpaid:
     POST /api/session-payments/enrollment/{enrollmentId}/session/{sessionId}/mark-unpaid

3. GET REPORTS:
   - Get payment summary for an enrollment:
     GET /api/session-payments/enrollment/{enrollmentId}/summary

=== Database Schema ===
The session_payments table tracks:
- enrollment_id: Links to student's enrollment
- session_id: Links to specific session
- is_paid: Boolean payment status
- payment_date: When payment was made
- payment_amount: Amount paid for this session
- payment_method: How payment was made
- transaction_reference: Payment reference
- notes: Additional notes
- marked_by: User who marked the payment

=== Payment Policy Logic ===
- Per Session: Each session has its own payment amount (price_per_session)
- Full Training: Payment amount is calculated as (price_full / total_sessions)
- Automatic amount calculation based on training policy
`);
}

// Run tests if this file is executed directly
if (require.main === module) {
  showUsageExamples();
  // Uncomment to run actual tests (requires valid UUIDs and auth token)
  // testSessionPayments();
}

module.exports = { testSessionPayments, showUsageExamples }; 