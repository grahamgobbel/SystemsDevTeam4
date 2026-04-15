# TCU Ambassador Scheduling System - Requirements & Design

## Business Requirements Overview

This document outlines the key business rules and system design considerations for the TCU Ambassador Scheduling system based on input from TCU Admissions.

### Tour Guide Scheduling Targets

#### Annual Workforce
- **Spring Semester**: 85-95 ambassadors employed
- **Fall Semester**: 75-85 ambassadors employed
- Total capacity: 75-95 depending on semester

#### Tour Guide Distribution Per Shift
- **Minimum per shift**: 4-5 guides
- **Maximum per shift**: 6-10 guides depending on day

#### Shift Intensity Levels
**High-Volume Days** (More guides needed):
- **Friday**: 6-10 ambassadors per slot (biggest day)
- **Monday PM & Thursday PM**: 5-8 ambassadors per slot (bigger days)

**Medium-Volume Days**:
- **Monday AM & Wednesday AM**: 5-8 ambassadors (group tour rotations - schedule more for rotation)
- **Other days/times**: 4-6 ambassadors per slot

#### Gender Balance Requirement
- **Minimum male ambassadors per shift**: 2 guides per shift

#### Tour Types
- **Group Tours**: Monday AM, Wednesday AM (require more guides for rotation)
- **Individual Tours**: All other slots

### Scheduling Frequency & Availability

#### Scheduling Cycle
- **Frequency**: By semester (not weekly or monthly)
- **Spring semester**: January - May
- **Fall semester**: August - December

#### Availability Submission
- **Frequency**: Semesterly
- Ambassadors submit their availability once per semester
- System tracks submission deadlines per semester

### Database Schema Design

#### Core Tables

**users**
- tracks ambassador profiles and employment status
- new fields: `gender`, `current_semester`
- supports 75-95 employee tracking

**tours**
- new fields: `semester`, `shift_type`
- tracks which semester each tour belongs to
- identifies tour type (group vs individual)

**shift_parameters**
- Stores capacity rules per day/time combination
- Enforces minimum and maximum ambassador allocation
- Tracks group tour identifiers
- Attributes:
  - `day`: Day of week
  - `time_slot`: Time (e.g., "10:00 AM", "02:00 PM")
  - `min_ambassadors`: Minimum guides needed
  - `max_ambassadors`: Maximum guides assignable
  - `min_male_ambassadors`: Minimum male guides needed
  - `shift_type`: Optional shift classification
  - `is_group_tour`: Flag for group tour rotation

**availability_periods**
- Manages submission windows per semester
- Attributes:
  - `semester`: Semester identifier
  - `start_date`: Availability period start
  - `end_date`: Availability period end
  - `submission_deadline`: When ambassadors must submit

**availability_slots** (existing, now semester-aware)
- Ambassador time availability
- Linked to submission periods

**tour_assignments** (existing)
- Tracks ambassador-to-tour assignments

### Current Shift Parameters Configured

```
Monday 10 AM:    MIN 5 | MAX 8  | MIN MALE 2 | GROUP TOUR
Monday 2 PM:     MIN 5 | MAX 8  | MIN MALE 2
Tuesday 10 AM:   MIN 4 | MAX 6  | MIN MALE 2
Tuesday 2 PM:    MIN 4 | MAX 6  | MIN MALE 2
Wednesday 10 AM: MIN 5 | MAX 8  | MIN MALE 2 | GROUP TOUR
Wednesday 2 PM:  MIN 4 | MAX 6  | MIN MALE 2
Thursday 10 AM:  MIN 4 | MAX 6  | MIN MALE 2
Thursday 2 PM:   MIN 5 | MAX 8  | MIN MALE 2 (BIGGER)
Friday 10 AM:    MIN 6 | MAX 10 | MIN MALE 2 (BUSIEST)
Friday 2 PM:     MIN 6 | MAX 10 | MIN MALE 2 (BUSIEST)
```

### Seasonality Considerations

The system is designed to handle seasonal variations:
- Spring typically has higher demand (85-95 ambassadors)
- Fall typically has lower demand (75-85 ambassadors)
- This is managed through:
  - Different availability submission periods per semester
  - Semester-specific tour scheduling
  - Flexible shift parameters per season if needed

### Feature Implementation Notes

#### Gender Tracking
- Ambassadors' gender is tracked to ensure balanced representation
- System infers gender from names on initial seed but allows manual override in profile
- Scheduling logic can enforce minimum male representation per shift

#### Semester-Based Scheduling
- Each tour is tagged with a semester
- Each ambassador has a `current_semester` field
- Availability submissions are tied to specific semesters
- Enables clean separation between spring and fall schedules

#### Group Tour Rotations
- Monday AM and Wednesday AM are identified as group tour times
- System can track which tour belongs to a rotation group
- Helps ensure sufficient ambassadors for multiple rotations

### Future Enhancements

1. **Automated Scheduling Algorithm**: Use shift parameters to automatically assign ambassadors
2. **Conflict Detection**: Check ambassador availability against assignments
3. **Report Generation**: Gender balance reports, utilization rates by day/time
4. **Notification System**: Alerts for unfilled tours, scheduling conflicts
5. **Ambassador Rating System**: Track performance for scheduling preference
6. **Dynamic Availability**: Allow intra-semester availability adjustments
