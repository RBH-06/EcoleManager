const http = require('http');

// Test data for registration
const testData = JSON.stringify({
  email: "admin@school.com",
  password: "password123",
  first_name: "Admin",
  last_name: "User",
  phone: "1234567890",
  role: "admin"
});

// Test health check
console.log('Testing health check...');
const healthCheck = http.get('http://localhost:3000/', (res) => {
  let data = '';
  res.on('data', (chunk) => {
    data += chunk;
  });
  res.on('end', () => {
    console.log('Health check response:', data);
    console.log('Status:', res.statusCode);
    
    // Test registration after health check
    testRegistration();
  });
});

healthCheck.on('error', (err) => {
  console.error('Health check error:', err.message);
});

function testRegistration() {
  console.log('\nTesting registration...');
  
  const options = {
    hostname: 'localhost',
    port: 3000,
    path: '/api/auth/register',
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Content-Length': Buffer.byteLength(testData)
    }
  };

  const req = http.request(options, (res) => {
    let data = '';
    res.on('data', (chunk) => {
      data += chunk;
    });
    res.on('end', () => {
      console.log('Registration response:', data);
      console.log('Status:', res.statusCode);
      console.log('Headers:', res.headers);
    });
  });

  req.on('error', (err) => {
    console.error('Registration error:', err.message);
  });

  req.write(testData);
  req.end();
} 