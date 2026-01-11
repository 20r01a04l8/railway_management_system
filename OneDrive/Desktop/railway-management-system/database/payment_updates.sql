-- Add balance column to credit_cards table
ALTER TABLE credit_cards ADD COLUMN balance DECIMAL(10, 2) NOT NULL DEFAULT 100000.00;

-- Create UPI IDs table
CREATE TABLE upi_ids (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    upi_id VARCHAR(100) NOT NULL,
    balance DECIMAL(10, 2) NOT NULL DEFAULT 100000.00,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_upi_id (upi_id)
);

-- Create card transactions table
CREATE TABLE card_transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    card_id INT NOT NULL,
    transaction_type VARCHAR(20) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    description VARCHAR(255),
    reference_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (card_id) REFERENCES credit_cards(id) ON DELETE CASCADE,
    INDEX idx_card_id (card_id),
    INDEX idx_created_at (created_at)
);

-- Create UPI transactions table
CREATE TABLE upi_transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    upi_id INT NOT NULL,
    transaction_type VARCHAR(20) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    description VARCHAR(255),
    reference_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (upi_id) REFERENCES upi_ids(id) ON DELETE CASCADE,
    INDEX idx_upi_id (upi_id),
    INDEX idx_created_at (created_at)
);