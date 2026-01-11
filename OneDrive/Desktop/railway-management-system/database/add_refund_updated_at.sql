-- Add updated_at column to refund_requests table
ALTER TABLE refund_requests ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;