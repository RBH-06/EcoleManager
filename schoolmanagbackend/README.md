# Training School Management System – Backend API

## Overview

This is the backend API for the Training School Management System. It provides endpoints for authentication, user, student, teacher, training, class, session, enrollment, attendance, and payment management.

- **Base URL:** `http://localhost:3000/api/`
- **Authentication:** JWT (token in `Authorization: Bearer <token>` header)
- **Database:** PostgreSQL (Dockerized)

---

## Getting Started

### 1. Environment Setup
- Copy `.env.example` to `.env` and adjust values if needed.
- Ensure your Postgres Docker container is running and accessible at the credentials in `.env`.

### 2. Install Dependencies
```sh
npm install
```

### 3. Run Database Migration
- Connect to your Postgres database and run the migration script:

**Using psql:**
```sh
psql -h localhost -U admin -d schoolmanagement -f db_schema.sql
```
- Enter your password (`admin`) when prompted.

### 4. Start the Server
```sh
npm start
```

---

## Authentication

- **Register (Admin only, first time):**  
  `POST /api/auth/register`  
  ```json
  {
    "email": "admin@school.com",
    "password": "password123",
    "first_name": "Admin",
    "last_name": "User",
    "phone": "1234567890",
    "role": "admin"
  }
  ```

- **Login:**  
  `POST /api/auth/login`  
  ```json
  {
    "email": "admin@school.com",
    "password": "password123"
  }
  ```
  **Response:**  
  ```json
  {
    "token": "<JWT_TOKEN>",
    "user": { ... }
  }
  ```

- Use the returned `token` in the `Authorization` header for all protected endpoints.

---

## User Roles

- **admin**: Full access (manage users, students, teachers, trainings, classes, etc.)
- **subadmin**: Limited management access
- **teacher**: Access to their classes, students, attendance
- **student**: Access to their own profile, enrollments, attendance, payments

---

## Key Endpoints

### Users (Admin only)
- `POST /api/users` – Create subadmin/teacher/student
- `GET /api/users` – List users
- `GET /api/users/:id` – Get user by ID
- `PUT /api/users/:id` – Update user
- `DELETE /api/users/:id` – Delete user

### Students
- `POST /api/students`
- `GET /api/students`
- `GET /api/students/:id`
- `PUT /api/students/:id`
- `DELETE /api/students/:id`

### Teachers
- `POST /api/teachers`
- `GET /api/teachers`
- `GET /api/teachers/:id`
- `PUT /api/teachers/:id`
- `DELETE /api/teachers/:id`

### Trainings
- `POST /api/trainings`
- `GET /api/trainings`
- `GET /api/trainings/:id`
- `PUT /api/trainings/:id`
- `DELETE /api/trainings/:id`

### Classes
- `POST /api/classes`
- `GET /api/classes`
- `GET /api/classes/:id`
- `PUT /api/classes/:id`
- `DELETE /api/classes/:id`

### Sessions
- `POST /api/sessions`
- `GET /api/sessions`
- `GET /api/sessions/:id`
- `PUT /api/sessions/:id`
- `DELETE /api/sessions/:id`

### Enrollments
- `POST /api/enrollments`
- `GET /api/enrollments`
- `GET /api/enrollments/:id`
- `PUT /api/enrollments/:id`
- `DELETE /api/enrollments/:id`

### Attendance
- `POST /api/attendance`
- `GET /api/attendance`
- `GET /api/attendance/:id`
- `PUT /api/attendance/:id`
- `DELETE /api/attendance/:id`

### Payments
- `POST /api/payments`
- `GET /api/payments`
- `GET /api/payments/:id`
- `PUT /api/payments/:id`
- `DELETE /api/payments/:id`

---

## Common Headers

```http
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

---

## Error Handling

- All errors return JSON with a `message` field.
- 401: Unauthorized (invalid/missing token)
- 403: Forbidden (insufficient permissions)
- 404: Not found
- 400: Validation errors

---

## Notes

- All dates should be in ISO 8601 format (`YYYY-MM-DD`).
- IDs are UUIDs.
- For relationships (e.g., enrollments), use the referenced entity’s ID.

---

For any questions about endpoints, required fields, or authentication, please contact the backend team.
