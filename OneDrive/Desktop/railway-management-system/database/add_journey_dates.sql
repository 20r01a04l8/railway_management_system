-- Add journey dates to bookings table
ALTER TABLE bookings 
ADD COLUMN journey_date_from DATE NOT NULL DEFAULT '2024-01-01',
ADD COLUMN journey_date_to DATE NOT NULL DEFAULT '2024-01-01';

-- Update existing records with schedule date
UPDATE bookings b
JOIN train_schedules ts ON b.schedule_id = ts.id
SET b.journey_date_from = ts.schedule_date,
    b.journey_date_to = ts.schedule_date;

-- Remove default values after updating existing records
ALTER TABLE bookings 
ALTER COLUMN journey_date_from DROP DEFAULT,
ALTER COLUMN journey_date_to DROP DEFAULT;