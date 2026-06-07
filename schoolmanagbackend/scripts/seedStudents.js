
const pool = require('../src/config/database');


const firstNames = ['Amine', 'Nour', 'Yacine', 'Lina', 'Walid', 'Sara', 'Rania', 'Omar', 'Sofiane', 'Imene', 'Nesrine', 'Adel', 'Khaled', 'Yasmine', 'Farid', 'Samir', 'Meriem', 'Nadir', 'Sabrina', 'Reda', 'Karima', 'Amina', 'Mohamed', 'Salim', 'Hichem', 'Fouad', 'Nadia', 'Samira', 'Karim', 'Noureddine', 'Hakim', 'Nadia', 'Amina', 'Fatima', 'Ali', 'Rachid', 'Lila', 'Said', 'Nora', 'Mokhtar', 'Meriem', 'Lamia', 'Samia', 'Rachida', 'Souad', 'Zohra', 'Malika', 'Djamila', 'Kheira', 'Latifa'];
const lastNames = ['Benkhelifa', 'Belkacem', 'Zerrouki', 'Boumediene', 'Meziane', 'Boudiaf', 'Saadi', 'Boumediene', 'Brahimi', 'Boumediene', 'Boumediene', 'Boumediene', 'Boumediene', 'Boumediene', 'Boumediene', 'Boumediene', 'Boumediene', 'Boumediene', 'Boumediene', 'Boumediene', 'Boumediene', 'Boumediene', 'Boumediene', 'Boumediene', 'Boumediene', 'Boumediene', 'Boumediene', 'Boumediene', 'Boumediene', 'Boumediene', 'Boumediene', 'Boumediene', 'Boumediene', 'Boumediene', 'Boumediene', 'Boumediene', 'Boumediene', 'Boumediene', 'Boumediene', 'Boumediene', 'Boumediene', 'Boumediene', 'Boumediene', 'Boumediene', 'Boumediene', 'Boumediene', 'Boumediene', 'Boumediene', 'Boumediene', 'Boumediene'];

const students = [];
for (let i = 1; i <= 100; i++) {
  const first_name = firstNames[i % firstNames.length] + (i > firstNames.length ? `_${i}` : '');
  const last_name = lastNames[i % lastNames.length] + (i > lastNames.length ? `_${i}` : '');
  students.push({
    first_name,
    last_name,
    email: `${first_name.toLowerCase()}.${last_name.toLowerCase()}${i}@example.dz`,
    phone: `+2136${(60000000 + i).toString().padStart(8, '0')}`,
    registration_date: '2025-07-15',
    notes: 'Étudiant algérien',
    bday: `200${Math.floor(Math.random()*10)}-${String(Math.floor(Math.random()*12)+1).padStart(2,'0')}-${String(Math.floor(Math.random()*28)+1).padStart(2,'0')}`,
    parentname: `Parent_${first_name}`,
    parentphone: `+2136${(70000000 + i).toString().padStart(8, '0')}`
  });
}

async function seed() {
  for (const student of students) {
    await pool.query(
      `INSERT INTO students (first_name, last_name, email, phone, registration_date, notes, bday, parentname, parentphone)
       VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)`,
      [
        student.first_name,
        student.last_name,
        student.email,
        student.phone,
        student.registration_date,
        student.notes,
        student.bday,
        student.parentname,
        student.parentphone
      ]
    );
  }
  console.log('Algerian students seeded!');
  process.exit();
}

seed().catch(e => { console.error(e); process.exit(1); });
