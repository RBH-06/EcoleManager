-- ENUM TYPES
CREATE TYPE user_role AS ENUM ('admin', 'sub_admin');
CREATE TYPE user_status AS ENUM ('active', 'inactive', 'suspended');
CREATE TYPE student_status AS ENUM ('active', 'inactive', 'graduated', 'dropped');
CREATE TYPE teacher_status AS ENUM ('active', 'inactive', 'on_leave');
CREATE TYPE permission_type AS ENUM (
    'manage_trainings',
    'manage_students', 
    'view_payments',
    'manage_attendance',
    'view_reports',
    'manage_schedules'
);
CREATE TYPE training_status AS ENUM ('active', 'inactive', 'completed', 'cancelled');
CREATE TYPE assignment_status AS ENUM ('active', 'inactive');
CREATE TYPE class_status AS ENUM ('scheduled', 'ongoing', 'completed', 'cancelled');
CREATE TYPE session_status AS ENUM ('scheduled', 'ongoing', 'completed', 'cancelled');
CREATE TYPE payment_type_enum AS ENUM ('full_training', 'per_session');
CREATE TYPE enrollment_status AS ENUM ('active', 'completed', 'dropped', 'suspended');
CREATE TYPE attendance_status AS ENUM ('present', 'absent', 'late', 'excused');
CREATE TYPE payment_method_enum AS ENUM ('cash', 'card', 'bank_transfer', 'online');
CREATE TYPE payment_status AS ENUM ('pending', 'completed', 'failed', 'refunded');

-- USERS
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    role user_role NOT NULL DEFAULT 'sub_admin',
    status user_status NOT NULL DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- STUDENTS
CREATE TABLE students (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(20),
    date_of_birth DATE,
    address TEXT,
    emergency_contact_name VARCHAR(200),
    emergency_contact_phone VARCHAR(20),
    emergency_contact_relationship VARCHAR(100),
    parent_guardian_name VARCHAR(200),
    parent_guardian_phone VARCHAR(20),
    parent_guardian_email VARCHAR(255),
    medical_notes TEXT,
    status student_status DEFAULT 'active',
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- TEACHERS
CREATE TABLE teachers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(20) NOT NULL,
    specializations TEXT[],
    hire_date DATE DEFAULT CURRENT_DATE,
    hourly_rate DECIMAL(8,2),
    bio TEXT,
    qualifications TEXT,
    status teacher_status DEFAULT 'active',
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- SUB-ADMIN PERMISSIONS
CREATE TABLE sub_admin_permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    permission permission_type NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- TRAININGS
CREATE TABLE trainings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    duration_weeks INTEGER,
    total_sessions INTEGER,
    price_full DECIMAL(10,2),
    price_per_session DECIMAL(10,2),
    max_students INTEGER,
    status training_status DEFAULT 'active',
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- TEACHER-TRAINING ASSIGNMENTS
CREATE TABLE teacher_trainings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    teacher_id UUID REFERENCES teachers(id) ON DELETE CASCADE,
    training_id UUID REFERENCES trainings(id) ON DELETE CASCADE,
    assigned_date DATE DEFAULT CURRENT_DATE,
    status assignment_status DEFAULT 'active',
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(teacher_id, training_id)
);

-- TRAINING CLASSES/BATCHES
CREATE TABLE training_classes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    training_id UUID REFERENCES trainings(id) ON DELETE CASCADE,
    teacher_id UUID REFERENCES teachers(id),
    name VARCHAR(200) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    schedule_days INTEGER[],
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    max_students INTEGER,
    status class_status DEFAULT 'scheduled',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- SESSIONS
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    class_id UUID REFERENCES training_classes(id) ON DELETE CASCADE,
    session_number INTEGER NOT NULL,
    scheduled_date DATE NOT NULL,
    scheduled_start_time TIME NOT NULL,
    scheduled_end_time TIME NOT NULL,
    actual_start_time TIME,
    actual_end_time TIME,
    topic VARCHAR(200),
    notes TEXT,
    status session_status DEFAULT 'scheduled',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ENROLLMENTS
CREATE TABLE enrollments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    class_id UUID REFERENCES training_classes(id) ON DELETE CASCADE,
    enrollment_date DATE DEFAULT CURRENT_DATE,
    payment_type payment_type_enum NOT NULL,
    sessions_purchased INTEGER,
    sessions_used INTEGER DEFAULT 0,
    status enrollment_status DEFAULT 'active',
    enrolled_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ATTENDANCE
CREATE TABLE attendance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    enrollment_id UUID REFERENCES enrollments(id) ON DELETE CASCADE,
    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
    status attendance_status NOT NULL,
    check_in_time TIMESTAMP,
    check_out_time TIMESTAMP,
    notes TEXT,
    marked_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- PAYMENTS
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    enrollment_id UUID REFERENCES enrollments(id) ON DELETE CASCADE,
    amount DECIMAL(10,2) NOT NULL,
    payment_method payment_method_enum,
    payment_date DATE DEFAULT CURRENT_DATE,
    due_date DATE,
    status payment_status DEFAULT 'pending',
    transaction_reference VARCHAR(100),
    notes TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- INDEXES
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_sub_admin_permissions_user_id ON sub_admin_permissions(user_id);
CREATE INDEX idx_students_email ON students(email);
CREATE INDEX idx_students_phone ON students(phone);
CREATE INDEX idx_students_status ON students(status);
CREATE INDEX idx_students_created_by ON students(created_by);
CREATE INDEX idx_teachers_email ON teachers(email);
CREATE INDEX idx_teachers_status ON teachers(status);
CREATE INDEX idx_teacher_trainings_teacher_id ON teacher_trainings(teacher_id);
CREATE INDEX idx_teacher_trainings_training_id ON teacher_trainings(training_id);
CREATE INDEX idx_trainings_status ON trainings(status);
CREATE INDEX idx_training_classes_training_id ON training_classes(training_id);
CREATE INDEX idx_training_classes_teacher_id ON training_classes(teacher_id);
CREATE INDEX idx_training_classes_start_date ON training_classes(start_date);
CREATE INDEX idx_sessions_class_id ON sessions(class_id);
CREATE INDEX idx_sessions_scheduled_date ON sessions(scheduled_date);
CREATE INDEX idx_enrollments_student_id ON enrollments(student_id);
CREATE INDEX idx_enrollments_class_id ON enrollments(class_id);
CREATE INDEX idx_enrollments_enrolled_by ON enrollments(enrolled_by);
CREATE INDEX idx_attendance_enrollment_id ON attendance(enrollment_id);
CREATE INDEX idx_attendance_session_id ON attendance(session_id);
CREATE INDEX idx_payments_enrollment_id ON payments(enrollment_id);
CREATE INDEX idx_payments_status ON payments(status);
CREATE INDEX idx_payments_payment_date ON payments(payment_date);
