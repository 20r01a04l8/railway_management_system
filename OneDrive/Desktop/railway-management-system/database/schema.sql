-- Railway Management System Database Schema
-- Normalized design following 3NF principles

-- Users table for authentication and user management
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    role ENUM('admin', 'user') DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Stations table
CREATE TABLE stations (
    id INT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    city VARCHAR(255) NOT NULL,
    state VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trains table
CREATE TABLE trains (
    id INT PRIMARY KEY AUTO_INCREMENT,
    number VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    type ENUM('express', 'passenger', 'superfast') NOT NULL,
    total_seats INT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Routes table - defines train routes
CREATE TABLE routes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    train_id INT NOT NULL,
    source_station_id INT NOT NULL,
    destination_station_id INT NOT NULL,
    departure_time TIME NOT NULL,
    arrival_time TIME NOT NULL,
    distance_km INT NOT NULL,
    base_fare DECIMAL(10,2) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (train_id) REFERENCES trains(id),
    FOREIGN KEY (source_station_id) REFERENCES stations(id),
    FOREIGN KEY (destination_station_id) REFERENCES stations(id)
);

-- Train schedules - specific train runs on specific dates
CREATE TABLE train_schedules (
    id INT PRIMARY KEY AUTO_INCREMENT,
    route_id INT NOT NULL,
    schedule_date DATE NOT NULL,
    available_seats INT NOT NULL,
    status ENUM('scheduled', 'running', 'completed', 'cancelled') DEFAULT 'scheduled',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (route_id) REFERENCES routes(id),
    UNIQUE KEY unique_route_date (route_id, schedule_date)
);

-- Bookings table
CREATE TABLE bookings (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    schedule_id INT NOT NULL,
    booking_reference VARCHAR(20) UNIQUE NOT NULL,
    passenger_count INT NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    status ENUM('confirmed', 'cancelled', 'completed') DEFAULT 'confirmed',
    booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (schedule_id) REFERENCES train_schedules(id)
);

-- Passengers table - normalized passenger details
CREATE TABLE passengers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    booking_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    age INT NOT NULL,
    gender ENUM('male', 'female', 'other') NOT NULL,
    seat_number VARCHAR(10),
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE
);

-- Refund requests table
CREATE TABLE refund_requests (
    id INT PRIMARY KEY AUTO_INCREMENT,
    booking_id INT NOT NULL,
    user_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_at TIMESTAMP NULL,
    admin_id INT NULL,
    rejection_reason TEXT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (admin_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_refund_requests_booking (booking_id),
    INDEX idx_refund_requests_user (user_id),
    INDEX idx_refund_requests_status (status),
    INDEX idx_refund_requests_requested (requested_at)
);

-- System alerts table
CREATE TABLE system_alerts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    alert_type ENUM('info', 'warning', 'danger', 'success') NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    icon VARCHAR(50) DEFAULT 'info-circle',
    dismissible BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_trains_number ON trains(number);
CREATE INDEX idx_routes_train ON routes(train_id);
CREATE INDEX idx_schedules_date ON train_schedules(schedule_date);
CREATE INDEX idx_bookings_user ON bookings(user_id);
CREATE INDEX idx_bookings_reference ON bookings(booking_reference);