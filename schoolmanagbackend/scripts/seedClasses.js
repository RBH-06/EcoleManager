require('dotenv').config();
const pool = require('../src/config/database');

async function getId(table) {
  const res = await pool.query(`SELECT id FROM ${table} LIMIT 1`);
  return res.rows[0] ? res.rows[0].id : null;
}

async function seedClasses() {

  // Use real teacher and training IDs
  const teacherIds = [
    '07615691-3a7e-4ad4-b0f1-79e1882c7c9b',
    '0ea5bbad-2b2e-4d0f-b20a-84277c22247c',
    '10bc9d2c-9020-44a7-87fd-7fd0cb45b49a',
    '307f6be4-b0cd-4abb-bbe1-7c63c6988663',
    '3c8fbe0b-ed50-4f03-8440-944f8f1b00ae',
    '4101bff6-0466-43eb-ba93-fce6c12a1c84',
    '419665b5-f20f-47fc-86d8-99438aa349b6',
    '4689e8e5-b451-4a6f-8ad9-4d57105b0e61',
    '5b63e106-7058-4d61-a689-5e8af9634dbe',
    '71c29811-d7a5-4c91-bf54-a7c279569ba7'
  ];
  const trainingIds = [
    '1174bb4d-1e7c-4487-becc-5eba24b0d581',
    '4a67978c-a0dc-4df7-b139-12cb534e8045',
    '8ff40758-ba73-48d7-9efb-8573b50149eb',
    'dca4bb06-2c30-4ad4-bbc0-47910ae5e5e1',
    'e50fbfe2-b062-4b50-a7b2-0f429119f61a',
    'f496b44f-42ba-4e81-ba65-30e4e881eb32'
  ];
  const classNames = [
    'Python Programming', 'Mathematics Level 1', 'Physics Basics', 'Chemistry Intro', 'Biology Essentials',
    'History of Algeria', 'French Language', 'English Conversation', 'Computer Science', 'Philosophy'
  ];
  const classes = [];
  for (let i = 0; i < 10; i++) {
    classes.push({
      name: `${classNames[i]} - Batch ${String.fromCharCode(65 + i)}`,
      training_id: trainingIds[i % trainingIds.length],
      teacher_id: teacherIds[i % teacherIds.length],
      start_date: `2025-0${(i%6)+1}-01`,
      end_date: `2025-0${(i%6)+2}-28`,
      status: 'scheduled'
    });
  }

  for (const c of classes) {
    try {
      await pool.query(
        `INSERT INTO training_classes (name, training_id, teacher_id, start_date, end_date, status) VALUES ($1,$2,$3,$4,$5,$6)`,
        [c.name, c.training_id, c.teacher_id, c.start_date, c.end_date, c.status]
      );
      console.log(`Inserted: ${c.name}`);
    } catch (err) {
      console.error(`Failed to insert ${c.name}:`, err.message);
    }
  }
  await pool.end();
  console.log('Classes seeded.');
}

seedClasses();
