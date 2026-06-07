# Teacher Deletion Scenarios and Best Practices

## Overview

This document explains how the system handles teacher deletion scenarios and provides best practices for managing teacher departures.

## Current Database Behavior

### Foreign Key Constraints
- `training_classes.teacher_id` references `teachers.id` with `ON DELETE SET NULL`
- This means when a teacher is deleted, their classes remain but `teacher_id` becomes `NULL`
- Classes are not automatically deleted when a teacher is removed

## Scenarios and Solutions

### Scenario 1: Teacher with No Active Classes
**What happens:** Teacher can be safely deleted
**Solution:** Use hard delete
```http
DELETE /api/teachers/{teacherId}
```

### Scenario 2: Teacher with Active Classes
**What happens:** System prevents deletion and shows active classes
**Solutions:**

#### Option A: Soft Delete (Recommended)
Mark teacher as inactive without deleting:
```http
POST /api/teachers/{teacherId}/soft-delete
```

#### Option B: Reassign Classes
Move all classes to another teacher:
```http
POST /api/teachers/reassign-classes
{
  "fromTeacherId": "uuid",
  "toTeacherId": "uuid"
}
```

#### Option C: Cancel Classes and Delete
Cancel all classes and then delete teacher:
```http
POST /api/teachers/{teacherId}/handle-departure
{
  "cancelClasses": true
}
```

## API Endpoints

### Check Deletion Status
```http
GET /api/teachers/{teacherId}/check-deletion
```
**Response:**
```json
{
  "canDelete": false,
  "hasActiveClasses": true,
  "activeClasses": [...],
  "message": "Teacher has active classes. Use soft delete instead."
}
```

### Get Teacher with Dependencies
```http
GET /api/teachers/{teacherId}/with-dependencies
```
**Response:**
```json
{
  "teacher": {...},
  "hasActiveClasses": true,
  "activeClasses": [...],
  "canDelete": false,
  "canDeactivate": false
}
```

### Get Active Classes
```http
GET /api/teachers/{teacherId}/active-classes
```

### Soft Delete
```http
POST /api/teachers/{teacherId}/soft-delete
```

### Handle Teacher Departure
```http
POST /api/teachers/{teacherId}/handle-departure
{
  "cancelClasses": false,
  "reassignToTeacherId": "uuid"
}
```

## Best Practices

### 1. Always Check Before Deleting
Use the check-deletion endpoint to understand the impact:
```javascript
const response = await fetch(`/api/teachers/${teacherId}/check-deletion`);
const data = await response.json();

if (!data.canDelete) {
  console.log('Teacher has active classes:', data.activeClasses);
  // Handle accordingly
}
```

### 2. Use Soft Delete by Default
Soft delete preserves data and allows for easy reactivation:
```javascript
// Instead of DELETE, use soft delete
await fetch(`/api/teachers/${teacherId}/soft-delete`, {
  method: 'POST'
});
```

### 3. Plan Class Reassignment
When a teacher leaves, plan their class reassignment:
```javascript
// Reassign all classes to another teacher
await fetch('/api/teachers/reassign-classes', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    fromTeacherId: departingTeacherId,
    toTeacherId: newTeacherId
  })
});
```

### 4. Handle Emergency Departures
For sudden departures, cancel classes if no replacement is available:
```javascript
await fetch(`/api/teachers/${teacherId}/handle-departure`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    cancelClasses: true
  })
});
```

## Data Recovery

### Recovering Soft-Deleted Teachers
Soft-deleted teachers can be reactivated by updating their status:
```http
PUT /api/teachers/{teacherId}
{
  "status": "active"
}
```

### Recovering Classes with NULL Teacher
Classes with `teacher_id = NULL` can be reassigned:
```http
PUT /api/training-classes/{classId}
{
  "teacher_id": "new-teacher-uuid"
}
```

## Monitoring and Alerts

### Recommended Monitoring
1. **Classes without teachers:** Query for `training_classes` where `teacher_id IS NULL`
2. **Inactive teachers with active classes:** Monitor for data inconsistencies
3. **Deletion attempts:** Log all teacher deletion attempts for audit purposes

### Example Queries
```sql
-- Find classes without teachers
SELECT * FROM training_classes WHERE teacher_id IS NULL AND status IN ('scheduled', 'ongoing');

-- Find inactive teachers with active classes
SELECT t.*, COUNT(tc.id) as active_class_count
FROM teachers t
JOIN training_classes tc ON t.id = tc.teacher_id
WHERE t.status = 'inactive' AND tc.status IN ('scheduled', 'ongoing')
GROUP BY t.id;
```

## Security Considerations

1. **Audit Trail:** All teacher deletion operations are logged
2. **Permission Checks:** Only admins can delete teachers
3. **Data Validation:** System validates dependencies before allowing deletion
4. **Rollback Capability:** Soft delete allows for easy recovery

## Error Handling

### Common Error Responses
```json
{
  "error": "Cannot delete teacher with active classes",
  "activeClasses": [...],
  "suggestion": "Use soft delete instead or reassign classes first"
}
```

### Handling Errors in Frontend
```javascript
try {
  const response = await fetch(`/api/teachers/${teacherId}`, {
    method: 'DELETE'
  });
  
  if (!response.ok) {
    const error = await response.json();
    if (error.activeClasses) {
      // Show reassignment options
      showReassignmentDialog(error.activeClasses);
    }
  }
} catch (error) {
  console.error('Failed to delete teacher:', error);
}
``` 