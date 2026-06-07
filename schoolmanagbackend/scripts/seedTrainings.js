require('dotenv').config();
const Training = require('../src/models/Training');
const pool = require('../src/config/database');


async function seedTrainings() {
  const trainings = [
    {
      name: 'Mathématiques BAC',
      description: 'Préparation intensive au BAC algérien en mathématiques.',
      total_sessions: 20,
      price_per_session: 1500,
      total_price: null,
      max_students: 25,
      paymentpolicy: 'per session'
    },
    {
      name: 'Anglais Conversation',
      description: 'Cours de conversation anglaise pour lycéens et universitaires.',
      total_sessions: 12,
      price_per_session: 1200,
      total_price: null,
      max_students: 20,
      paymentpolicy: 'per session'
    },
    {
      name: 'Sciences Physiques BAC',
      description: 'Cours de soutien en sciences physiques pour terminale.',
      total_sessions: 18,
      price_per_session: null,
      total_price: 20000,
      max_students: 30,
      paymentpolicy: 'at once'
    },
    {
      name: 'Informatique Débutant',
      description: 'Initiation à l’informatique pour collégiens.',
      total_sessions: 10,
      price_per_session: 1000,
      total_price: null,
      max_students: 15,
      paymentpolicy: 'per session'
    },
    {
      name: 'Prépa Médecine',
      description: 'Préparation aux concours de médecine en Algérie.',
      total_sessions: 25,
      price_per_session: null,
      total_price: 35000,
      max_students: 20,
      paymentpolicy: 'at once'
    }
  ];

  for (const t of trainings) {
    try {
      await pool.query(
        `INSERT INTO trainings (name, description, total_sessions, price_per_session, total_price, max_students, paymentpolicy)
         VALUES ($1,$2,$3,$4,$5,$6,$7)`,
        [
          t.name,
          t.description,
          t.total_sessions,
          t.price_per_session,
          t.total_price,
          t.max_students,
          t.paymentpolicy
        ]
      );
      console.log(`Inserted: ${t.name}`);
    } catch (err) {
      console.error(`Failed to insert ${t.name}:`, err.message);
    }
  }
  await pool.end();
  console.log('5 Algerian context trainings seeded!');
}

seedTrainings();
