"""
Create sample data for testing the dashboard
"""
from services.student_service import create_student
from services.class_service import create_class, enroll_student
from services.attendance_service import get_or_create_session
from services.fees_service import set_fee_rule, generate_invoices_for_session
from datetime import datetime, timedelta


def create_sample_data():
    """Create sample students, classes, and sessions for dashboard testing"""
    
    print("Creating sample data...")
    
    # Create sample classes
    classes_data = [
        {"name": "6ème A", "level": "Collège", "section": "A", "room": "101", "academic_year": "2024-2025"},
        {"name": "5ème B", "level": "Collège", "section": "B", "room": "102", "academic_year": "2024-2025"},
        {"name": "4ème A", "level": "Collège", "section": "A", "room": "103", "academic_year": "2024-2025"},
        {"name": "3ème C", "level": "Collège", "section": "C", "room": "104", "academic_year": "2024-2025"},
    ]
    
    class_ids = []
    for class_data in classes_data:
        try:
            class_id = create_class(class_data)
            class_ids.append(class_id)
            print(f"Created class: {class_data['name']} (ID: {class_id})")
            
            # Set fee rule for each class
            set_fee_rule(class_id, 5000, "MAD")  # 50 MAD per session
            print(f"Set fee rule for class {class_data['name']}: 50 MAD")
            
        except Exception as e:
            print(f"Error creating class {class_data['name']}: {e}")
    
    # Create sample students
    students_data = [
        {"first_name": "Ahmed", "last_name": "Benali", "date_of_birth": "2010-03-15", "gender": "M", 
         "address": "123 Rue Hassan II, Casablanca", "phone": "0612345678", "email": "parent1@gmail.com"},
        {"first_name": "Fatima", "last_name": "Alaoui", "date_of_birth": "2009-07-22", "gender": "F", 
         "address": "456 Avenue Mohammed V, Rabat", "phone": "0687654321", "email": "parent2@gmail.com"},
        {"first_name": "Youssef", "last_name": "Kadiri", "date_of_birth": "2010-11-08", "gender": "M", 
         "address": "789 Boulevard Zerktouni, Marrakech", "phone": "0654123987", "email": "parent3@gmail.com"},
        {"first_name": "Aicha", "last_name": "Bennani", "date_of_birth": "2009-05-30", "gender": "F", 
         "address": "321 Rue Ibn Battuta, Fès", "phone": "0698765432", "email": "parent4@gmail.com"},
        {"first_name": "Omar", "last_name": "Tazi", "date_of_birth": "2010-09-12", "gender": "M", 
         "address": "654 Avenue Lalla Yacout, Casablanca", "phone": "0611223344", "email": "parent5@gmail.com"},
        {"first_name": "Khadija", "last_name": "Idrissi", "date_of_birth": "2009-12-03", "gender": "F", 
         "address": "987 Rue El Jadida, Rabat", "phone": "0677889900", "email": "parent6@gmail.com"},
    ]
    
    student_ids = []
    for student_data in students_data:
        try:
            student_id = create_student(student_data)
            student_ids.append(student_id)
            print(f"Created student: {student_data['first_name']} {student_data['last_name']} (ID: {student_id})")
        except Exception as e:
            print(f"Error creating student {student_data['first_name']}: {e}")
    
    # Enroll students in classes (randomly distribute)
    if class_ids and student_ids:
        enrollments = [
            (class_ids[0], [student_ids[0], student_ids[1]]),  # 6ème A
            (class_ids[1], [student_ids[2], student_ids[3]]),  # 5ème B  
            (class_ids[2], [student_ids[4]]),                  # 4ème A
            (class_ids[3], [student_ids[5]]),                  # 3ème C
        ]
        
        for class_id, students in enrollments:
            for student_id in students:
                try:
                    enroll_student(class_id, student_id)
                    print(f"Enrolled student {student_id} in class {class_id}")
                except Exception as e:
                    print(f"Error enrolling student {student_id}: {e}")
    
    # Create some attendance sessions (last week and this week)
    if class_ids:
        today = datetime.now().date()
        dates = [
            today - timedelta(days=7),
            today - timedelta(days=5), 
            today - timedelta(days=3),
            today - timedelta(days=1),
        ]
        
        for class_id in class_ids[:2]:  # Only for first 2 classes
            for date in dates:
                try:
                    session_id = get_or_create_session(class_id, date.isoformat())
                    print(f"Created session for class {class_id} on {date}")
                    
                    # Generate invoices for the session
                    generate_invoices_for_session(class_id, session_id)
                    print(f"Generated invoices for session {session_id}")
                    
                except Exception as e:
                    print(f"Error creating session: {e}")
    
    print("\n✅ Sample data creation completed!")
    print("Dashboard should now show:")
    print(f"- {len(student_ids)} students")
    print(f"- {len(class_ids)} classes") 
    print("- Recent sessions and invoices")
    print("- Activity feed with recent registrations")


if __name__ == "__main__":
    create_sample_data()