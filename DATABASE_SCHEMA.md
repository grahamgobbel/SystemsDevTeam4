# Database Schema Documentation

## Table: shift_parameters

Defines scheduling capacity rules for each day/time combination.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| day | TEXT | Day of week (Monday-Sunday) |
| time_slot | TEXT | Time in 'HH:MM AM/PM' format |
| min_ambassadors | INTEGER | Minimum guides to schedule (default: 4) |
| max_ambassadors | INTEGER | Maximum guides to assign (default: 6) |
| min_male_ambassadors | INTEGER | Minimum male guides required (default: 2) |
| shift_type | TEXT | Optional shift classification (e.g., "group_tour", "high_volume") |
| is_group_tour | INTEGER | Flag: 1 if group tour rotation, 0 if individual tours |

**Unique Constraint**: (day, time_slot, shift_type)

**Example Queries**:
```sql
-- Get parameters for Friday 10 AM
SELECT * FROM shift_parameters WHERE day = 'Friday' AND time_slot = '10:00 AM';

-- Find all group tour slots
SELECT day, time_slot FROM shift_parameters WHERE is_group_tour = 1;

-- Get slots requiring heavy staffing
SELECT day, time_slot, min_ambassadors FROM shift_parameters WHERE min_ambassadors >= 5;
```

---

## Table: availability_periods

Tracks the availability submission windows for each semester.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| semester | TEXT | Semester identifier (e.g., "Spring 2026", "Fall 2026") |
| start_date | TEXT | ISO date when availability period begins |
| end_date | TEXT | ISO date when availability period ends |
| submission_deadline | TEXT | ISO date by which ambassadors must submit |

**Unique Constraint**: (semester)

**Example Queries**:
```sql
-- Get current submission windows
SELECT * FROM availability_periods WHERE end_date >= date('now');

-- Get deadline for Spring 2026
SELECT submission_deadline FROM availability_periods WHERE semester = 'Spring 2026';

-- Find overdue availability submissions
SELECT * FROM availability_periods WHERE submission_deadline < date('now');
```

---

## Table: users (Enhanced)

Ambassador and admin account information.

### New Columns

| Column | Type | Description |
|--------|------|-------------|
| gender | TEXT | Ambassador gender (Male, Female, Non-binary, Prefer not to say) |
| current_semester | TEXT | Semester currently employed (e.g., "Spring 2026") |

### All Columns (for reference)

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| name | TEXT | Full name |
| email | TEXT | Email address (unique) |
| password | TEXT | Password hash/placeholder |
| role | TEXT | 'ambassador' or 'admin' |
| major | TEXT | Primary major |
| minor | TEXT | Minor (optional) |
| year | TEXT | Undergraduate year |
| personality | TEXT | Personality type (Introvert/Ambivert/Extrovert) |
| gender | TEXT | Gender identity |
| status | TEXT | Account status (Active/Inactive) |
| ambassador_since | TEXT | Date became ambassador |
| current_semester | TEXT | Current semester assignment |
| tours_completed | INTEGER | Lifetime tour count |
| total_hours | INTEGER | Lifetime hours worked |

---

## Table: tours (Enhanced)

Tour schedule records.

### New Columns

| Column | Type | Description |
|--------|------|-------------|
| semester | TEXT | Semester for this tour (e.g., "Spring 2026") |
| shift_type | TEXT | Tour type classification (optional) |

### All Columns (for reference)

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| tour_type | TEXT | Tour name/type |
| tour_date | TEXT | ISO date of tour |
| start_time | TEXT | Start time (HH:MM AM/PM) |
| end_time | TEXT | End time (HH:MM AM/PM) |
| location | TEXT | Tour meeting location |
| ambassadors_needed | INTEGER | Number of guides to schedule |
| published | INTEGER | 1 if schedule published, 0 if pending |
| semester | TEXT | Semester for this tour |
| shift_type | TEXT | Optional shift type |

**Example Queries**:
```sql
-- Get all tours for Spring 2026
SELECT * FROM tours WHERE semester = 'Spring 2026' ORDER BY tour_date;

-- Find unpublished tours
SELECT * FROM tours WHERE published = 0;

-- Get Friday tours with busiest times
SELECT * FROM tours WHERE tour_date LIKE '%-05' AND start_time = '10:00 AM';
```

---

## Table: availability_slots

Ambassador availability submissions (unchanged, but now semester-aware through availability_periods).

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| user_id | INTEGER | Ambassador ID (FK to users) |
| day | TEXT | Day of week availability |
| start_time | TEXT | Availability start time |
| end_time | TEXT | Availability end time |
| priority | TEXT | How full this slot can be (1st/2nd/3rd/Low Priority) |
| submitted | INTEGER | 1 if submitted in current period, 0 otherwise |

---

## Constants Defined

### Gender Options
```python
VALID_GENDERS = ["Male", "Female", "Non-binary", "Prefer not to say"]
```

### Semesters
```python
SEMESTERS = ["Spring 2026", "Fall 2026", "Spring 2027", "Fall 2027"]
```

### Days
```python
VALID_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
```

### Priority Levels
```python
VALID_PRIORITIES = ["1st Priority", "2nd Priority", "3rd Priority", "Low Priority"]
```

---

## Common Queries and Use Cases

### 1. Check Shift Capacity for Specific Tour
```sql
SELECT sp.min_ambassadors, sp.max_ambassadors, sp.min_male_ambassadors
FROM shift_parameters sp
WHERE sp.day = (SELECT strftime('%A', tours.tour_date) FROM tours WHERE tours.id = ?)
  AND sp.time_slot = tours.start_time;
```

### 2. Find Ambassadors for a Tour Slot
```sql
-- Find ambassadors available for a specific tour
SELECT users.id, users.name, users.gender, COUNT(ta.id) AS current_assignments
FROM users
LEFT JOIN tour_assignments ta ON ta.ambassador_id = users.id
WHERE users.current_semester = 'Spring 2026'
  AND users.gender IN ('Male', 'Female')  -- Can filter by gender
GROUP BY users.id
HAVING current_assignments < 5;  -- Not overbooked
```

### 3. Check Current Staffing Levels
```sql
-- Get current tour assignments by day/time
SELECT sp.day, sp.time_slot, COUNT(ta.id) AS assigned_count, sp.min_ambassadors, sp.max_ambassadors
FROM shift_parameters sp
LEFT JOIN tours t ON strftime('%A', t.tour_date) = sp.day 
                   AND t.start_time = sp.time_slot
                   AND t.semester = 'Spring 2026'
LEFT JOIN tour_assignments ta ON ta.tour_id = t.id
GROUP BY sp.day, sp.time_slot;
```

### 4. Verify Gender Balance
```sql
-- Check if shifts meet minimum male ambassador requirement
SELECT t.id, t.tour_type, t.tour_date, 
       COUNT(CASE WHEN u.gender = 'Male' THEN 1 END) AS male_count,
       COUNT(CASE WHEN u.gender != 'Male' THEN 1 END) AS other_count,
       sp.min_male_ambassadors
FROM tours t
LEFT JOIN tour_assignments ta ON ta.tour_id = t.id
LEFT JOIN users u ON u.id = ta.ambassador_id
LEFT JOIN shift_parameters sp ON sp.day = strftime('%A', t.tour_date) 
                               AND sp.time_slot = t.start_time
GROUP BY t.id
HAVING male_count < sp.min_male_ambassadors;
```

### 5. Semester Management
```sql
-- Switch ambassadors to new semester
UPDATE users SET current_semester = 'Fall 2026' WHERE current_semester = 'Spring 2026';

-- Clear availability for new semester
DELETE FROM availability_slots 
WHERE user_id IN (SELECT id FROM users WHERE current_semester = 'Fall 2026') 
  AND submitted = 0;
```
