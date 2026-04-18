# Requirements Document: TCU Ambassador Scheduling System

**Document Version**: 1.0  
**Date**: April 16, 2026  
**Prepared by**: Systems Development Team 4  

---

## 1. CLIENT ORGANIZATION

### Organization Overview
**Client**: Texas Christian University (TCU) Admissions Department

**Stakeholder**: TCU Admissions Office and Ambassador Program Coordinators

**Location**: Fort Worth, Texas

**Scope**: Admissions and student recruitment operations, specifically the Tour Guide Ambassador Program

### Client Context
TCU employs 75-95 student ambassadors per semester to conduct campus tours and represent the university to prospective students and visitors. The program requires sophisticated scheduling to balance ambassador availability, tour demand, and administrative workload while maintaining gender diversity and operational efficiency across multiple tour times and days.

---

## 2. PROBLEM BEING ADDRESSED

### Current Challenges
1. **Manual Scheduling**: Previous manual processes for matching ambassadors to tour slots were time-consuming and error-prone
2. **Availability Tracking**: Lack of centralized system to collect and manage ambassador availability
3. **Workload Distribution**: Difficulty ensuring equitable tour assignment and preventing ambassador overload
4. **Data Silos**: Ambassador information scattered across multiple spreadsheets and documents
5. **Compliance Issues**: No systematic way to enforce gender diversity requirements (minimum 2 male ambassadors per shift)
6. **Reporting Gaps**: Limited visibility into ambassador workload and performance metrics

### Business Impact
- Improved tour scheduling efficiency
- Better ambassador utilization and satisfaction
- Data-driven reporting for admissions metrics
- Role-based access control for administrators and ambassadors
- Centralized profile and performance tracking

---

## 3. APPLICATION'S KEY FEATURES

### 3.1 Authentication & Access Control
- **Email-based Login**: Secure authentication using TCU email addresses and encrypted passwords
- **Role-Based Access**: Separate dashboards and permissions for amphibassadors and administrators
- **Session Management**: Secure HTTP-only cookies with 8-hour expiration
- **Account Creation**: Self-service registration for new ambassadors

### 3.2 Ambassador Features

#### Dashboard
- Welcome screen with personalized greeting
- **Upcoming Assignments**: View scheduled tours with date, time, and location
- **Notifications**: Real-time alerts for schedule changes and new tour assignments
- **Monthly Stats**: Track monthly tour count, hours completed, and upcoming events
- **Quick Actions**: Fast links to submit availability or update profile

#### Availability Submission
- **Weekly View**: Set recurring availability by day of week and time slot
- **Priority Rankings**: Rate each time slot (1st Priority, 2nd Priority, 3rd Priority, Low Priority)
- **Dashboard Grid**: Visual calendar view of complete weekly availability
- **Semester-Based Submission**: Submit once per semester; system manages availability windows

#### Profile Management
- **Academic Information**: Update major, minor, and undergraduate year
- **Personality Assessment**: Document personality type (Introvert, Ambivert, Extrovert)
- **Tour Tracking**: View lifetime statistics (tours completed, total hours)
- **Profile Updates**: Persist changes to ambassador record in real-time

### 3.3 Administrator Features

#### Admin Dashboard
- **Tour Management**: Create, view, and publish tour schedules
- **Ambassador Roster**: Complete list of all ambassadors with filtering/search
- **Assignment Workload**: Visual report of ambassador workload distribution
- **Scheduling Tools**: Assign ambassadors to tours based on availability and constraints

#### Scheduling Administration
- **Shift Parameters**: Define scheduling rules by day/time (min/max ambassadors, gender requirements)
- **Tour Scheduling**: Publish and manage tour schedules for current semester
- **Availability Periods**: Set submission windows and deadlines for each semester
- **Batch Operations**: Manage multiple assignments and schedule updates

#### Reporting
- **Workload Report**: Visual dashboard showing ambassador tour assignments by volume and status
- **Roster Export**: Generate reports with ambassador demographics and performance
- **Compliance Tracking**: Verify gender diversity and shift minimum requirements

---

## 4. EXPECTED INPUTS AND OUTPUTS

### 4.1 System Inputs

#### Authentication
- **Input**: Email address and password
- **Processing**: Match against user database, validate credentials with PBKDF2-SHA256 hashing
- **Output**: Session token issued and stored in HttpOnly cookie

#### Ambassador Account Registration
- **Inputs**: 
  - Full name (text)
  - TCU email address (.edu domain validation)
  - Password (minimum 8 characters, hashed before storage)
  - Role selection (ambassador or admin)
- **Processing**: Validate unique email, hash password, create user record
- **Output**: Confirmation message, redirect to login or dashboard

#### Availability Submission
- **Inputs**:
  - Day of week (Monday-Sunday)
  - Start time (HH:MM AM/PM format)
  - End time (HH:MM AM/PM format)
  - Priority ranking (1st/2nd/3rd/Low)
- **Processing**: Store multiple availability slots per ambassador, link to current semester
- **Output**: Confirmation message, updated availability dashboard

#### Profile Updates
- **Inputs**:
  - Major (from predefined list)
  - Minor (from predefined list, optional)
  - Year (Freshman/Sophomore/Junior/Senior)
  - Personality type (Introvert/Ambivert/Extrovert)
- **Processing**: Validate major/minor codes, update user record
- **Output**: Confirmation message, profile card displays updated information

#### Tour Assignment (Admin)
- **Inputs**:
  - Tour date (ISO format)
  - Tour time (HH:MM AM/PM)
  - Ambassador IDs (one or more)
  - Shift type (optional classification)
- **Processing**: Record assignments, check availability conflicts, enforce constraints
- **Output**: Assignment confirmation, updated roster display

### 4.2 System Outputs

#### Authentication Response
- Login page with email/password form and "Create Account" link
- Dashboard upon successful login
- Redirect to login on session expiration

#### Ambassador Dashboard
- Personalized greeting with ambassador name
- **Upcoming Assignments Card**: List format with tour date, time, location
- **Notifications Sidebar**: Status updates and system messages
- **Monthly Stats Panel**: Aggregated metrics (total tours, hours, upcoming events)
- HTML table/card layout with responsive design

#### Availability Dashboard
- **Weekly Grid View**: 7-column calendar (Mon-Sun) × time slots with priority indicators
- **Edit Form**: Dropdown/input fields for each slot with save button
- **Confirmation Messages**: Green success banner or red error banner

#### Profile Page
- **Profile Card**: Name, email, tours completed count
- **Edit Form**: Dropdowns for major/minor, radio buttons for year/personality
- **Save Button**: POST form with confirmation feedback

#### Admin Workload Report
- **Visual Dashboard**: Bar chart or table showing assignment counts per ambassador
- **Filter Options**: Filter by role, status, tour type
- **Export Option**: Generate report data for external analysis

#### Logout
- Session token deleted from database
- Redirect to login page
- Cookie cleared from browser

---

## 5. DATA STORED IN THE DATABASE

### 5.1 Database Technology
**Database System**: SQLite 3  
**Location**: `/data/SQLite.db` (project root)  
**Schema Design**: Relational tables with foreign key constraints

### 5.2 Core Database Tables

#### Table: `users`
Stores ambassador and administrator account information.

| Column | Type | Purpose |
|--------|------|---------|
| id | INTEGER PRIMARY KEY | Unique user identifier |
| name | TEXT | Full name of ambassador/admin |
| email | TEXT UNIQUE | TCU email address (login identifier) |
| password | TEXT | PBKDF2-SHA256 hashed password |
| role | TEXT | 'ambassador' or 'admin' |
| major | TEXT | Primary academic major |
| minor | TEXT | Secondary academic minor (optional) |
| year | TEXT | Undergraduate year (Freshman/Sophomore/Junior/Senior) |
| personality | TEXT | Personality type (Introvert/Ambivert/Extrovert) |
| gender | TEXT | Gender identity (Male/Female/Non-binary/Prefer not to say) |
| status | TEXT | Account status (Active/Inactive) |
| ambassador_since | TEXT | Date became ambassador (ISO format) |
| current_semester | TEXT | Current employed semester (e.g., "Spring 2026") |
| tours_completed | INTEGER | Lifetime tour count |
| total_hours | INTEGER | Lifetime hours worked (decimal stored as integer × 100) |

**Constraints**: Email must be unique, role must be 'ambassador' or 'admin'

#### Table: `tours`
Represents scheduled tour instances.

| Column | Type | Purpose |
|--------|------|---------|
| id | INTEGER PRIMARY KEY | Unique tour identifier |
| tour_type | TEXT | Tour name/classification (e.g., "Group Tour", "Individual Tour") |
| tour_date | TEXT | ISO date of tour (YYYY-MM-DD) |
| start_time | TEXT | Start time in HH:MM AM/PM format |
| end_time | TEXT | End time in HH:MM AM/PM format |
| location | TEXT | Meeting location on campus |
| ambassadors_needed | INTEGER | Required number of guides |
| published | INTEGER | 1 if schedule published, 0 if draft |
| semester | TEXT | Semester assignment (e.g., "Spring 2026") |
| shift_type | TEXT | Optional shift classification |

**Constraints**: tour_date must be valid ISO format

#### Table: `assignments`
Links ambassadors to specific tours.

| Column | Type | Purpose |
|--------|------|---------|
| id | INTEGER PRIMARY KEY | Unique assignment identifier |
| tour_id | INTEGER FK | Reference to tours table |
| user_id | INTEGER FK | Reference to users table (ambassador) |
| assigned_date | TEXT | Date assignment was created (ISO format + timestamp) |
| status | TEXT | 'assigned', 'completed', 'cancelled' |

**Constraints**: Unique (tour_id, user_id) pair; foreign keys enforce referential integrity

#### Table: `availability_slots`
Ambassador availability submissions for scheduling.

| Column | Type | Purpose |
|--------|------|---------|
| id | INTEGER PRIMARY KEY | Unique availability record ID |
| user_id | INTEGER FK | Reference to users table |
| day | TEXT | Day of week (Monday-Sunday) |
| start_time | TEXT | Availability start time (HH:MM AM/PM) |
| end_time | TEXT | Availability end time (HH:MM AM/PM) |
| priority | TEXT | Preference level (1st/2nd/3rd/Low Priority) |
| submitted | INTEGER | 1 if submitted in current period, 0 otherwise |

**Constraints**: Foreign key to users table; one record per unique (user_id, day, start_time) combination

#### Table: `shift_parameters`
Scheduling rules for each day/time combination.

| Column | Type | Purpose |
|--------|------|---------|
| id | INTEGER PRIMARY KEY | Rule identifier |
| day | TEXT | Day of week (Monday-Sunday) |
| time_slot | TEXT | Time in HH:MM AM/PM format |
| min_ambassadors | INTEGER | Minimum guides to schedule (default: 4) |
| max_ambassadors | INTEGER | Maximum guides to assign (default: 6) |
| min_male_ambassadors | INTEGER | Minimum male guides required (default: 2) |
| shift_type | TEXT | Optional shift classification |
| is_group_tour | INTEGER | 1 if group tour, 0 if individual tours |

**Constraints**: Unique (day, time_slot, shift_type) combination

#### Table: `availability_periods`
Tracks submission windows for each semester.

| Column | Type | Purpose |
|--------|------|---------|
| id | INTEGER PRIMARY KEY | Period identifier |
| semester | TEXT UNIQUE | Semester name (e.g., "Spring 2026", "Fall 2026") |
| start_date | TEXT | Period start date (ISO format) |
| end_date | TEXT | Period end date (ISO format) |
| submission_deadline | TEXT | Deadline for availability submission (ISO format) |

**Constraints**: Semester field must be unique

#### Table: `sessions`
Secure session tokens for authenticated requests.

| Column | Type | Purpose |
|--------|------|---------|
| id | INTEGER PRIMARY KEY | Session record ID |
| token_hash | TEXT UNIQUE | SHA256 hash of session token (never store raw token) |
| user_id | INTEGER FK | Reference to users table |
| expires_at | INTEGER | Unix timestamp when session expires |
| created_at | INTEGER | Unix timestamp when session created |

**Constraints**: token_hash unique, foreign key to users table, automatic cleanup of expired sessions

#### Table: `notifications`
System notifications for ambassadors.

| Column | Type | Purpose |
|--------|------|---------|
| id | INTEGER PRIMARY KEY | Notification identifier |
| user_id | INTEGER FK | Recipient ambassador |
| type | TEXT | Notification type (e.g., "assignment", "schedule_change") |
| message | TEXT | Notification content |
| read_at | TEXT | ISO timestamp when read (NULL if unread) |
| created_at | TEXT | ISO timestamp creation |

### 5.3 Data Relationships

```
users (1) ──→ (many) assignments (many) ──→ (1) tours
users (1) ──→ (many) availability_slots
users (1) ──→ (many) sessions [authentication]
users (1) ──→ (many) notifications
shift_parameters (1) ──→ (many) tours [via day/time matching]
availability_periods (1) ──→ (many) availability_slots [via semester]
```

### 5.4 Sample Data Volumes

**Typical Production Scale** (Spring Semester):
- Users: 85-95 ambassadors + 3-5 admins = ~90-100 total
- Tours: 12-15 tours per week × 16 weeks = ~200 tours per semester
- Assignments: ~4-6 ambassadors per tour × 200 tours = ~800-1200 assignments
- Availability Slots: ~10-15 slots per ambassador × 85 ambassadors = ~1000-1275 records
- Sessions: 50-100 concurrent active sessions
- Notifications: 500-1000 per semester

---

## 6. SCREENSHOTS AND GUI SKETCHES

### 6.1 Login Page

```
╔════════════════════════════════════════════╗
║                                            ║
║              TCU                           ║
║                                            ║
║      Ambassador Scheduling                ║
║                                            ║
║  Sign in with your TCU email and password  ║
║                                            ║
║  ┌──────────────────────────────────────┐  ║
║  │ Email                                │  ║
║  │ john.doe@tcu.edu                     │  ║
║  └──────────────────────────────────────┘  ║
║                                            ║
║  ┌──────────────────────────────────────┐  ║
║  │ Password                             │  ║
║  │ ••••••••••••••••                     │  ║
║  └──────────────────────────────────────┘  ║
║                                            ║
║  ┌──────────────────────────────────────┐  ║
║  │         LOGIN                        │  ║
║  └──────────────────────────────────────┘  ║
║                                            ║
║  ┌──────────────────────────────────────┐  ║
║  │    CREATE ACCOUNT                    │  ║
║  └──────────────────────────────────────┘  ║
║                                            ║
║  Use your assigned account credentials     ║
║                                            ║
╚════════════════════════════════════════════╝
```

**Key Elements**:
- TCU logo badge (purple)
- Email input field with TCU email placeholder
- Password input field (masked)
- Primary action: Login button (purple, full-width)
- Secondary action: Create Account button (lighter purple, stands out)
- Helper text explaining credential requirements

### 6.2 Create Account Page

```
╔════════════════════════════════════════════╗
║                                            ║
║              TCU                           ║
║                                            ║
║        Create Account                      ║
║                                            ║
║    Set up your account using your          ║
║        school email.                       ║
║                                            ║
║  ┌──────────────────────────────────────┐  ║
║  │ Full Name *                          │  ║
║  │ Jane Doe                             │  ║
║  └──────────────────────────────────────┘  ║
║                                            ║
║  ┌──────────────────────────────────────┐  ║
║  │ Email *                              │  ║
║  │ jane.doe@tcu.edu                     │  ║
║  └──────────────────────────────────────┘  ║
║                                            ║
║  Account Role *                            ║
║  ◯ Ambassador                              ║
║  ◯ Admin                                   ║
║                                            ║
║  ┌──────────────────────────────────────┐  ║
║  │ Password * (min 8 chars)             │  ║
║  │ ••••••••••••••••                     │  ║
║  └──────────────────────────────────────┘  ║
║                                            ║
║  ┌──────────────────────────────────────┐  ║
║  │ Confirm Password *                   │  ║
║  │ ••••••••••••••••                     │  ║
║  └──────────────────────────────────────┘  ║
║                                            ║
║  ┌──────────────────────────────────────┐  ║
║  │      CREATE ACCOUNT                  │  ║
║  └──────────────────────────────────────┘  ║
║                                            ║
║  Back to Login                             ║
║                                            ║
╚════════════════════════════════════════════╝
```

**Key Elements**:
- Required field indicators (*)
- Text input for name
- Email validation (.edu domain)
- Radio buttons for role selection
- Password strength requirement (8 chars minimum)
- Confirm password field
- Create Account button
- Back to Login link

### 6.3 Ambassador Dashboard

```
╔══════════════════════════════════════════════════════════════╗
║  [TCU Logo] Ambassador Scheduling           [User Dropdown]  ║
║  Today, April 16, 2026                   [Logout]            ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Welcome, Jane Doe!                                          ║
║  Here's your schedule overview and latest updates            ║
║                                    [SUBMIT AVAILABILITY]     ║
║                                                              ║
║  ╔══════════════════════════════╦═══════════════════════╗   ║
║  ║  Upcoming Assignments   [>]  ║   Notifications       ║   ║
║  ╠══════════════════════════════╣═══════════════════════╣   ║
║  ║ Friday, April 18 @ 10:00 AM  ║ ✓ Assignment Updated  ║   ║
║  ║ Campus Tour – McNulty Center ║   Your Friday 10 AM   ║   ║
║  ║ 6 guides scheduled           ║   tour is confirmed   ║   ║
║  ║ [DETAILS]                    ║                       ║   ║
║  ║                              ║ • New Availability    ║   ║
║  ║ Monday, April 22 @ 2:00 PM   ║   Period Open         ║   ║
║  ║ Group Tour – Sadler Hall     ║   Submit by May 1     ║   ║
║  ║ 5 guides scheduled           ║                       ║   ║
║  ║ [DETAILS]                    ║ This Month            ║   ║
║  ║                              ║ ─────────────────     ║   ║
║  ║ Wednesday, April 24 @ 11 AM  ║ Total Tours: 3        ║   ║
║  ║ Individual Tour – Brite Lite ║ Hours Completed: 6.5  ║   ║
║  ║ 4 guides scheduled           ║ Upcoming Events: 2    ║   ║
║  ║ [DETAILS]                    ║                       ║   ║
║  ║                              ║                       ║   ║
║  ╚══════════════════════════════╩═══════════════════════╝   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

**Key Elements**:
- Top navigation with TCU branding and user menu
- Personalized greeting with ambassador name
- "Submit Availability" call-to-action button
- Left panel: Upcoming assignments in card format
  - Tour date/time and location
  - Number of guides scheduled
  - Details link
- Right sidebar: Notifications and monthly stats
  - Recent system updates
  - Month-to-date metrics (tours, hours, upcoming)

### 6.4 Availability Submission Page

```
╔══════════════════════════════════════════════════════════════╗
║  [TCU Logo] Ambassador Scheduling          [User Dropdown]   ║
║  Availability Submission                                    ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Submit Availability                                         ║
║  Set up your weekly schedule with preference rankings       ║
║                                                              ║
║  [Dashboard] [Weekly Availability]                          ║
║                                                              ║
║  ╔═══════════════════════════════════════════════════════╗   ║
║  ║ How it Works:                                         ║   ║
║  ║ • Weekly Availability: Set recurring weekly schedule  ║   ║
║  ║ • Preference Rankings: Rate each slot (1st/2nd/3rd)   ║   ║
║  ║ • Dashboard View: See your complete schedule          ║   ║
║  ╚═══════════════════════════════════════════════════════╝   ║
║                                                              ║
║  Weekly Availability Schedule                               ║
║  ┌──────────────────────────────────────────────────────┐   ║
║  │ Day: [Monday ▼]  Start: [9:00 AM ▼]  End: [5:00 PM]│   ║
║  │ Priority: [1st Priority ▼]         [SAVE] [DELETE]  │   ║
║  └──────────────────────────────────────────────────────┘   ║
║                                                              ║
║  ┌──────────────────────────────────────────────────────┐   ║
║  │ Day: [Tuesday ▼]  Start: [9:00 AM ▼]  End: [5:00 PM]│   ║
║  │ Priority: [2nd Priority ▼]        [SAVE] [DELETE]   │   ║
║  └──────────────────────────────────────────────────────┘   ║
║                                                              ║
║  [+ ADD MORE SLOTS]                 [SUBMIT FOR REVIEW]     ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

**Key Elements**:
- Tab navigation (Dashboard/Weekly Availability)
- Information panel explaining availability submission
- Repeating form groups for each availability slot
  - Day dropdown (Monday-Sunday)
  - Start/end time selectors
  - Priority ranking dropdown
  - Save/Delete buttons
- Add more slots button
- Submit for review button

### 6.5 Profile Management Page

```
╔══════════════════════════════════════════════════════════════╗
║  [TCU Logo] Ambassador Scheduling          [User Dropdown]   ║
║  Profile                                                    ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Ambassador Profile                                          ║
║  Update your info to help us match you with the right tours  ║
║                                                              ║
║  ╔══════════════════════╗  ╔════════════════════════════╗    ║
║  ║ Jane Doe             ║  ║ Academic Information       ║    ║
║  ║ jane.doe@tcu.edu     ║  ║ * Required fields          ║    ║
║  ║                      ║  ║                            ║    ║
║  ║ Tours Completed: 12  ║  ║ Major *                    ║    ║
║  ╚══════════════════════╝  ║ [Business Administration ▼]║    ║
║                             ║                            ║    ║
║                             ║ Minor (Optional)           ║    ║
║                             ║ [Marketing ▼]             ║    ║
║                             ║                            ║    ║
║                             ║ Year *                     ║    ║
║                             ║ ◯ Freshman ◯ Sophomore    ║    ║
║                             ║ ◯ Junior ◯ Senior         ║    ║
║                             ║                            ║    ║
║                             ║ Personality Type *         ║    ║
║                             ║ ◯ Introvert ◯ Ambivert    ║    ║
║                             ║ ◯ Extrovert               ║    ║
║                             ║                            ║    ║
║                             ║ [SAVE CHANGES]             ║    ║
║  ╚════════════════════════════════════════════════════════╝    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

**Key Elements**:
- Profile card sidebar showing name, email, tour count
- Edit form with required field indicators
- Major/minor dropdowns (pre-populated lists)
- Year radio buttons (Freshman through Senior)
- Personality type radio buttons
- Save changes button

### 6.6 Admin Dashboard

```
╔══════════════════════════════════════════════════════════════╗
║  [TCU Logo] TCU Admin Console              [User Dropdown]    ║
║  Dashboard                                                  ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Administrator Dashboard - Spring 2026 Scheduling            ║
║                                                              ║
║  ╔══════════════════╦══════════════╦═══════════════════╗    ║
║  ║ Tours Published  ║ Ambassadors  ║ % Assignments     ║    ║
║  ║ 38/48            ║ 87/92        ║ 94%               ║    ║
║  ║ [76 planned]     ║ [Active]     ║ [On schedule]     ║    ║
║  ╚══════════════════╩══════════════╩═══════════════════╝    ║
║                                                              ║
║  Quick Actions: [NEW TOUR] [MANAGE AMBASSADORS]             ║
║                  [VIEW AVAILABILITY] [GENERATE REPORT]       ║
║                                                              ║
║  Ambassador Workload Report                                 ║
║  Filter: [All Roles ▼]  [All Status ▼]  [APPLY]            ║
║                                                              ║
║  ┌─────────────────────────────────────────────────────┐    ║
║  │ Name             Email             Tours  Hours     │    ║
║  ├─────────────────────────────────────────────────────┤    ║
║  │ Jane Doe         jane.doe@tcu.edu   12    25.5h     │    ║
║  │ John Smith       j.smith@tcu.edu    8     16.0h     │    ║
║  │ Maria Garcia     m.garcia@tcu.edu   10    20.5h     │    ║
║  │ ...                                                 │    ║
║  │ [View All] [Export Report]                          │    ║
║  └─────────────────────────────────────────────────────┘    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

**Key Elements**:
- Key metrics dashboard (tours published, active ambassadors, assignment %)
- Quick action buttons for common admin tasks
- Workload report with filterable data
- Ambassador list with name, email, tour count, hours
- Export/view options for reporting

---

## 7. TECHNICAL SPECIFICATIONS

### 7.1 Technology Stack
- **Language**: Python 3.13+
- **Web Framework**: Native Python http.server (BaseHTTPRequestHandler)
- **Database**: SQLite 3
- **Authentication**: PBKDF2-SHA256 with 120,000 iterations
- **Session Management**: HttpOnly cookies + database token storage
- **Frontend**: HTML5, CSS3, responsive design
- **Server**: Localhost development server (127.0.0.1:8000)

### 7.2 Security Requirements
- ✓ Passwords hashed with PBKDF2-SHA256 (not stored in plain text)
- ✓ Session tokens hashed before database storage
- ✓ HttpOnly and SameSite cookie flags for CSRF/XSS mitigation
- ✓ 8-hour session expiration
- ✓ Input validation on all forms
- ✓ Email domain validation (.edu for TCU)
- ✓ Unique email enforcement at database level

### 7.3 Performance Targets
- Page load time: < 1 second (local development)
- Dashboard query response: < 500ms
- Database connection pool: 1 connection (single-threaded)
- Concurrent users: 50+ (testing environment)

### 7.4 Browser Compatibility
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- Mobile browsers (iOS Safari, Chrome Mobile)

---

## 8. ACCEPTANCE CRITERIA

### Authentication & Authorization
- [ ] Users can register with email, password, and role
- [ ] Login page displays with email/password fields
- [ ] Successful login creates session and redirects to dashboard
- [ ] Session persists across page navigation
- [ ] Session expires after 8 hours of inactivity
- [ ] Logout clears session and returns to login
- [ ] Role-based access prevents ambassadors from accessing admin pages
- [ ] Cannot register duplicate email addresses

### Ambassador Features
- [ ] Dashboard displays upcoming assignments
- [ ] Ambassador can submit weekly availability
- [ ] Availability slots can be edited/deleted
- [ ] Profile can be updated (major, minor, year, personality)
- [ ] Profile updates persist to database
- [ ] Monthly statistics display correctly

### Admin Features
- [ ] Admin can view complete ambassador roster
- [ ] Admin can create and publish tours
- [ ] Admin can assign ambassadors to tours
- [ ] Workload report generates with accurate data
- [ ] Shift parameters enforce minimum/maximum constraints
- [ ] Gender diversity requirements enforced

### Data Integrity
- [ ] All user data persists to SQLite database
- [ ] Foreign key relationships maintained
- [ ] Availability linked to correct ambassador
- [ ] Session tokens stored as hashes
- [ ] No sensitive data in logs or browser storage

---

## 9. FUTURE ENHANCEMENTS

### Phase 2
- **Automatic Scheduling Algorithm**: ML-based ambassador assignment
- **Email Notifications**: Send tour confirmations and schedule updates
- **Mobile App**: Native iOS/Android application
- **Calendar Sync**: Export to Google Calendar/Outlook
- **Analytics Dashboard**: Detailed performance metrics and trends

### Phase 3
- **Multi-semester Planning**: Look-ahead availability submissions
- **Feedback System**: Tour ratings and ambassador reviews
- **Audit Logging**: Complete system activity trail
- **API Layer**: RESTful API for third-party integrations
- **Tour Customization**: Custom tour types and pricing models

---

## 10. SIGN-OFF

**Document Prepared By**: Systems Development Team 4  
**Date**: April 16, 2026  
**Status**: Approved for Development  

**Client Approval**:  
___________________________  
TCU Admissions Department Representative  

**Development Team Approval**:  
___________________________  
Project Manager, Systems Development Team 4
