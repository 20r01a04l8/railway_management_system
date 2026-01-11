-- Sample data for Railway Management System

-- Insert sample stations
INSERT IGNORE INTO stations (code, name, city, state) VALUES
('DEL', 'New Delhi', 'Delhi', 'Delhi'),
('MUM', 'Mumbai Central', 'Mumbai', 'Maharashtra'),
('BLR', 'Bangalore City', 'Bangalore', 'Karnataka'),
('CHN', 'Chennai Central', 'Chennai', 'Tamil Nadu'),
('KOL', 'Kolkata', 'Kolkata', 'West Bengal'),
('HYD', 'Hyderabad', 'Hyderabad', 'Telangana'),
('PUN', 'Pune Junction', 'Pune', 'Maharashtra'),
('AHM', 'Ahmedabad Junction', 'Ahmedabad', 'Gujarat'),
('JAI', 'Jaipur Junction', 'Jaipur', 'Rajasthan'),
('LKO', 'Lucknow', 'Lucknow', 'Uttar Pradesh');

-- Insert sample trains
INSERT IGNORE INTO trains (number, name, type, total_seats) VALUES
('12001', 'Shatabdi Express', 'superfast', 200),
('12002', 'Rajdhani Express', 'superfast', 300),
('12003', 'Duronto Express', 'express', 250),
('12004', 'Jan Shatabdi', 'express', 180),
('12005', 'Garib Rath', 'passenger', 400),
('12006', 'Vande Bharat', 'superfast', 180),
('12007', 'Tejas Express', 'express', 220),
('12008', 'Humsafar Express', 'express', 280);

-- Insert sample routes
INSERT IGNORE INTO routes (train_id, source_station_id, destination_station_id, departure_time, arrival_time, distance_km, base_fare) VALUES
(1, 1, 2, '06:00:00', '14:30:00', 1384, 2500.00),
(1, 2, 1, '15:30:00', '23:45:00', 1384, 2500.00),
(2, 1, 3, '20:00:00', '06:30:00', 2168, 3200.00),
(2, 3, 1, '21:00:00', '07:15:00', 2168, 3200.00),
(3, 1, 4, '22:30:00', '10:45:00', 2180, 2800.00),
(4, 2, 3, '05:45:00', '22:15:00', 1279, 1800.00),
(5, 1, 5, '23:55:00', '19:20:00', 1472, 1200.00),
(6, 1, 7, '07:30:00', '12:15:00', 280, 1500.00),
(6, 7, 1, '18:00:00', '22:45:00', 280, 1500.00),
(7, 2, 8, '09:15:00', '18:30:00', 525, 2200.00),
(7, 8, 2, '20:00:00', '05:15:00', 525, 2200.00),
(8, 1, 9, '16:45:00', '21:30:00', 308, 1800.00),
(8, 9, 1, '06:30:00', '11:15:00', 308, 1800.00),
(1, 3, 6, '08:00:00', '20:30:00', 1290, 2800.00),
(2, 4, 5, '19:30:00', '08:45:00', 1663, 3500.00),
(3, 2, 6, '14:15:00', '02:30:00', 1166, 2400.00),
(4, 5, 4, '11:00:00', '23:15:00', 1659, 2600.00),
(5, 6, 3, '13:45:00', '05:00:00', 1290, 2200.00),
-- Mumbai routes
(1, 2, 4, '07:15:00', '19:45:00', 1338, 2600.00),
(2, 2, 5, '21:30:00', '14:15:00', 1968, 3400.00),
(3, 2, 6, '10:30:00', '22:00:00', 1166, 2400.00),
(6, 2, 7, '12:00:00', '16:30:00', 280, 1400.00),
-- Chennai routes
(1, 4, 2, '20:00:00', '08:30:00', 1338, 2600.00),
(2, 4, 3, '15:45:00', '01:30:00', 346, 1800.00),
(3, 4, 5, '18:30:00', '12:15:00', 1665, 3200.00),
(4, 4, 6, '09:00:00', '21:30:00', 1290, 2500.00),
-- Kolkata routes
(1, 5, 2, '16:00:00', '08:45:00', 1968, 3400.00),
(2, 5, 3, '12:30:00', '02:15:00', 1659, 3100.00),
(3, 5, 4, '14:15:00', '07:30:00', 1665, 3200.00),
(4, 5, 6, '22:00:00', '10:30:00', 1472, 2800.00),
-- Hyderabad routes
(1, 6, 2, '23:30:00', '11:00:00', 1166, 2400.00),
(2, 6, 3, '06:45:00', '18:15:00', 1290, 2500.00),
(3, 6, 4, '13:00:00', '01:30:00', 1290, 2500.00),
(4, 6, 5, '11:15:00', '23:45:00', 1472, 2800.00),
-- Bangalore routes
(1, 3, 2, '17:30:00', '05:45:00', 1279, 2400.00),
(2, 3, 4, '08:15:00', '19:45:00', 346, 1800.00),
(3, 3, 5, '19:00:00', '12:30:00', 1659, 3100.00),
(4, 3, 6, '21:45:00', '09:15:00', 1290, 2500.00);

-- Insert sample schedules for next 30 days
INSERT INTO train_schedules (route_id, schedule_date, available_seats)
SELECT 
    r.id,
    DATE_ADD(CURDATE(), INTERVAL seq.seq DAY),
    t.total_seats
FROM routes r
JOIN trains t ON r.train_id = t.id
CROSS JOIN (
    SELECT 0 as seq UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION 
    SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9 UNION
    SELECT 10 UNION SELECT 11 UNION SELECT 12 UNION SELECT 13 UNION SELECT 14 UNION
    SELECT 15 UNION SELECT 16 UNION SELECT 17 UNION SELECT 18 UNION SELECT 19 UNION
    SELECT 20 UNION SELECT 21 UNION SELECT 22 UNION SELECT 23 UNION SELECT 24 UNION
    SELECT 25 UNION SELECT 26 UNION SELECT 27 UNION SELECT 28 UNION SELECT 29
) seq
WHERE r.is_active = TRUE;

-- Insert admin user (username: admin, password: admin123)
INSERT IGNORE INTO users (username, email, password_hash, full_name, role) VALUES
('admin', 'admin@railway.com', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'System Administrator', 'admin');

-- Insert sample user (username: user, password: user123)
INSERT IGNORE INTO users (username, email, password_hash, full_name, phone) VALUES
('user', 'user@example.com', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'John Doe', '+91-9876543210');