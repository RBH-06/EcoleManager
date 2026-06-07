require('dotenv').config();
const pool = require('../src/config/database');

// 100 students, 10 classes (10 students per class)
const studentIds = [
  '046a32cb-64bd-4020-b9d0-4ef37379d619','07349152-fc3c-4bc9-9986-92b30b5cf0a4','08df59b7-253a-4542-bddb-aafe4dce00da','091a4473-2c57-479b-a38d-c46d9a463f5f','099136b8-1951-4605-b1db-6d28d7e35221','0b0e5e34-a441-4b07-86c9-fae3fcde83a7','0b96214b-2da4-4d46-a6ac-e61acd3aec53','0cc24825-9449-41a0-9e80-a4cdce18cc7f','0dc7b8c7-577b-422f-9094-bd66767545c8','13572af6-296a-45fc-99d0-0f4f387cf3a0','13fe5122-76cc-43be-9a0d-bf58f0176e29','167d7dbc-b679-42ec-8e52-420210bf386b','17254824-9658-4fc9-8a23-a006c3cf47ae','19e1e56f-91b4-40cc-ab83-9547f47b787b','22861c30-9d55-4074-a48e-33bcd34129ac','253949d6-0a28-419b-b0e8-c0835cafd2f2','256c0a13-6629-4cc1-85cc-57d353361e13','27ea76bc-cbdc-4368-aa2c-469637284f26','291b4a52-c41b-4afa-bfd1-041325bd1eaf','2a055930-d1b6-4cb5-9bfb-875e4dbe0529','2f62e2d4-c615-4830-be7e-4b838baf4ee5','2f6cb373-1643-4005-a4ff-a070366e13ed','30f0dbce-7002-40ed-82d0-3f6b19773d0b','345c66bf-e2ae-4764-a2f6-993a8572c157','36d8033d-431b-4ecb-94ba-59e7dea94477','374f3420-23da-45a9-9322-c9ea5817f9fb','39b490b6-1b6e-4275-8809-47d35c2d06d6','3a7d0312-f340-451c-8251-3ad8eb411210','3a8b5506-3943-4daf-b0ee-110098ec5785','3ee9cfd1-6d03-4836-bfbe-67da8226b9ca','4110aa09-d49e-4231-953d-611bef6dcf65','428f4dc5-a2b9-4af7-8129-d64e2abe7bbc','42ff33fc-ce95-4ef5-9ed5-222b82a48e3a','43849fe2-57ee-4c08-87a5-629d0263cf28','442511f6-c452-41fb-814b-3d332e88f55b','442c8c9c-cf32-4196-ad97-42db101eee26','4f81703e-be66-4148-a2c4-3c39d05325ae','508602b0-c1df-4f82-856e-c710c5e0ad72','5312321c-940c-43ac-a2ee-7cf1915d2a50','536d7b1b-00e9-481d-b11f-acb1d80946a5','56a0d9c8-05cd-4f68-b2ac-e6a894c515be','58de8b25-a200-49d7-b720-e75d92d44898','5b38afb4-a58b-4f31-a020-b12febbe84e5','5dd7cf5a-03d7-4d73-a2a0-c2eb2328ecc6','61e18d1f-a837-4cf0-9249-9b440921f264','63af0682-b83f-4629-82c6-7e0c339d8757','67b79dbc-4bdd-4275-bc14-f3607521e13e','6b07875e-68fa-4c95-bca2-b9dcce35d887','712e4f9d-cd78-46f7-8e23-d0ac345c4845','75035b7c-8882-4753-a48a-781be145570b','78726db7-2803-4471-bbff-e92836996ed1','7c5d13c6-d2d4-4d5f-919c-f3318cdd1497','7c65ef2d-bc57-4c55-9bd2-e68611cb85eb','7db7d3bb-0dcc-43ab-82af-68fa54d4298a','7f010e1f-3443-44c0-806f-1de1b9513af3','848a11e2-a49d-4ccf-a676-bcbbec524d72','8521a9fe-ef61-4f92-988e-2f3ebdcbd165','87338d69-3577-4b89-9102-f22ba96c2930','8f1c19e4-bfd9-4764-b145-4e7003687def','8f6e830b-d427-429d-ba9a-1d2c9c473e2f','92d28bf5-46ff-4c70-aa41-ed6d613f3cef','9f6ed0b7-a131-417c-9ce2-e090090b3db3','9fbb3c3a-39bd-423a-a409-a7b3db6697bf','a1ef2a97-b8c9-4a52-9f6a-3310db4bb17f','a7e601e2-5012-4567-8555-45c445ecb6d0','a8f2c729-8a58-49ca-92a7-9c9ec9640584','aab75564-cc00-4247-8457-98d1e207aaf7','ab648fe1-f90d-4207-95b1-ea3da435e0bc','acec1707-d4d0-4e7a-8926-f282abb58e2b','af8a70a9-f861-4e86-bec0-690f17ac6b2e','b24b808c-03de-4d64-bf98-12707688fc6d','b32bffe8-c478-4d47-aed3-e47f9fcf20a6','b574ead0-afc6-4674-bfc6-cf77d6a286c4','b73a8db3-2438-4bba-ba20-1c33749aa379','b9bc8e0f-5bdc-47b7-9a95-10dd4f60c2b8','ba415286-a8b9-4644-b545-06ef09bdea2e','ba52ee06-db42-4fa6-9409-5bc8bc06969f','bb3d22d9-1047-43e8-b262-8a82daffb78a','bbc46f48-4090-4937-9140-aca6cc22bc2a','c9b7da49-e13c-475c-8b7e-f947448a3c52','cadfc97b-a6c7-431f-b56f-18c29a94431a','cb3cd102-bee8-4601-b758-3a5684f65815','d26795d1-46ea-44be-91b5-02d42f45f6b8','d2b000b0-08f6-470b-963d-e7722c9d72a0','d37ea7ea-ec03-4230-8bb2-ff757407af31','d56bf7a3-af04-481c-a43d-7ba7cfdbe823','db0e7d59-18b8-4e8a-a708-8e5042370ef5','dced8826-7eb1-4aaa-a0e0-45cf1c40a0f7','ddb290e6-84ef-44cb-9bc6-c3b12bbd2a41','ddc0bf7b-8335-40c8-a552-ffed2fa11c93','de1bf913-95cf-4665-a160-09f8c3784683','e3549b1a-3b17-49e2-b356-7a7119fc782e','e6e9fdd6-c59f-49be-85cc-5fab95328682','e788de65-8a86-4177-8744-54905ea12f0c','eb87e4f0-6c7e-4cba-af56-afaf78a0575f','ec2b2e8a-868b-4599-84f0-a75b133ee116','ef969fd1-1298-41e2-a27b-39ebb139db42','f0322cc5-fce1-458c-a2f9-505fea0156d7','f3600fda-b57d-4640-8f5f-778607b77429','f4260205-575c-4909-89b9-d59e3582e0d0'
];
const classIds = [
  '039081a2-230a-4dab-ab11-65cf1a5bf097','16c2e2f0-b0de-4868-be0f-6449cc5ddce8','22972174-05af-4fa7-af87-1ce6955da0cf','23ed78cb-8830-424c-a2fb-0477d5f37701','32892702-7cba-4d21-883f-44369b7b4946','614c5d94-4c42-4360-b340-bec14e3d46d3','7eefa850-7fd8-4550-9046-02e622dcbcd6','97f5b054-251c-475f-873d-9c500d5b12a6','9a4dee4f-031b-450d-b14a-381363949942','dedfd4b2-e58d-4ac7-9317-6f59c970da71'
];

async function seedEnrollments() {
  let count = 0;
  for (let i = 0; i < studentIds.length; i++) {
    const student_id = studentIds[i];
    const class_id = classIds[i % classIds.length];
    try {
      await pool.query(
        'INSERT INTO enrollments (student_id, class_id, enrollment_date) VALUES ($1, $2, NOW())',
        [student_id, class_id]
      );
      count++;
    } catch (err) {
      if (!err.message.includes('duplicate')) {
        console.error(`Failed to enroll student ${student_id} in class ${class_id}:`, err.message);
      }
    }
  }
  await pool.end();
  console.log(`${count} enrollments inserted.`);
}

seedEnrollments();
