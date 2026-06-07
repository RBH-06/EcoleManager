require('dotenv').config();
const Teacher = require('../src/models/Teacher');
const pool = require('../src/config/database');

async function seedTeachers() {

  const firstNames = ['Redouane', 'Karim', 'Samira', 'Abdelkader', 'Nadia', 'Yacine', 'Amina', 'Meriem', 'Sofiane', 'Lina', 'Omar', 'Rania', 'Hakim', 'Noureddine', 'Salim', 'Fatima', 'Ali', 'Rachid', 'Lila', 'Said'];
  const lastNames = ['Slamani', 'Zerrouki', 'Bensalem', 'Mokhtari', 'Boumediene', 'Saadi', 'Belkacem', 'Boudiaf', 'Boumediene', 'Brahimi', 'Meziane', 'Benkhelifa', 'Belkacem', 'Boumediene', 'Boumediene', 'Boumediene', 'Boumediene', 'Boumediene', 'Boumediene', 'Boumediene'];
  const teachers = [];
  for (let i = 1; i <= 20; i++) {
    const first_name = firstNames[i % firstNames.length] + (i > firstNames.length ? `_${i}` : '');
    const last_name = lastNames[i % lastNames.length] + (i > lastNames.length ? `_${i}` : '');
    teachers.push({
      first_name,
      last_name,
      email: `${first_name.toLowerCase()}.${last_name.toLowerCase()}${i}@school.com`,
      phone: `07${(70000000 + i).toString().padStart(8, '0')}`,
      hire_date: `2025-${String(Math.floor(Math.random()*12)+1).padStart(2,'0')}-${String(Math.floor(Math.random()*28)+1).padStart(2,'0')}`,
      status: 'active'
    });
  }

  for (const t of teachers) {
    try {
      await Teacher.create(t);
      console.log(`Inserted: ${t.email}`);
    } catch (err) {
      console.error(`Failed to insert ${t.email}:`, err.message);
    }
  }
  await pool.end();
  console.log('20 Algerian teachers inserted.');
}

seedTeachers();
