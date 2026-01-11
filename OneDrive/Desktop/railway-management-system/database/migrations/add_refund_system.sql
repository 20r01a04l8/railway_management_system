-- Add refund requests and system alerts tables
-- Migration for adding refund management functionality

-- Refund requests table
CREATE TABLE IF NOT EXISTS refund_requests (
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
CREATE TABLE IF NOT EXISTS system_alerts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    alert_type ENUM('info', 'warning', 'danger', 'success') NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    icon VARCHAR(50) DEFAULT 'info-circle',
    dismissible BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);