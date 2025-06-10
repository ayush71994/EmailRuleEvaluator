CREATE DATABASE IF NOT EXISTS EMAIL_MANAGER; -- Create new database if it does not exist
USE EMAIL_MANAGER;
CREATE TABLE EMAILS (
    id VARCHAR(255) PRIMARY KEY,             -- Internal ID
    vendor_id VARCHAR(255) UNIQUE,           -- Gmail's message ID
    sender VARCHAR(512),             -- Sender's email address
    receiver VARCHAR(512),           -- Receiver's email address ( For now only supporting single receiver)
    subject TEXT,                            -- Email subject,  can be larger hence using Text
    received_at DATETIME,                    -- Time email is received in UTC
    raw_headers JSON,                         -- Store raw headers for future proofing
    current_folder VARCHAR(255) DEFAULT 'INBOX'   -- By default each email's current folder would be 'INBOX'
);