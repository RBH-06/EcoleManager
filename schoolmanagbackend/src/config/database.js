const { Pool } = require('pg');

console.log('DATABASE_URL:', process.env.DATABASE_URL);

// Parse the connection string manually to debug
const url = new URL(process.env.DATABASE_URL);
console.log('Parsed URL:', {
  host: url.hostname,
  port: url.port,
  database: url.pathname.slice(1),
  user: url.username,
  password: url.password ? '***' : 'undefined'
});

const pool = new Pool({
  host: url.hostname,
  port: url.port,
  database: url.pathname.slice(1),
  user: url.username,
  password: url.password,
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false,
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});

module.exports = pool;
