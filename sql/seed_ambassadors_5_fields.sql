-- Seed dataset with exactly 5 source fields per row:
-- name, email, major, year, involvement_level
--
-- Usage:
-- sqlite3 /tmp/SystemsDevTeam4/SQLite.db < sql/seed_ambassadors_5_fields.sql

BEGIN TRANSACTION;

WITH ambassador_dataset(name, email, major, year, involvement_level) AS (
    VALUES
        ('Avery Mitchell', 'avery.mitchell@tcu.edu', 'Marketing', 'Sophomore', 'High'),
        ('Jordan Lee', 'jordan.lee@tcu.edu', 'Finance', 'Junior', 'Medium'),
        ('Riley Carter', 'riley.carter@tcu.edu', 'Computer Science', 'Senior', 'High'),
        ('Taylor Nguyen', 'taylor.nguyen@tcu.edu', 'Accounting', 'Freshman', 'Low'),
        ('Morgan Davis', 'morgan.davis@tcu.edu', 'Management', 'Junior', 'Medium'),
        ('Cameron Brooks', 'cameron.brooks@tcu.edu', 'Economics', 'Senior', 'High'),
        ('Skyler Ramos', 'skyler.ramos@tcu.edu', 'Business Information Systems', 'Sophomore', 'Medium'),
        ('Parker Collins', 'parker.collins@tcu.edu', 'Supply Chain Management', 'Freshman', 'Low')
)
INSERT OR IGNORE INTO users (
    name,
    email,
    password,
    role,
    major,
    minor,
    year,
    personality,
    status,
    ambassador_since,
    tours_completed,
    total_hours
)
SELECT
    name,
    email,
    '',
    'ambassador',
    major,
    NULL,
    year,
    involvement_level,
    'Active',
    CAST(strftime('%Y', 'now') AS TEXT),
    0,
    0
FROM ambassador_dataset;

COMMIT;
