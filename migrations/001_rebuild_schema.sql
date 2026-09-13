USE local_tailor_connect;

-- ============================================================
-- Local Tailor Connect
-- Migration 001: Rebuild application schema compatibility
--
-- IMPORTANT:
-- This migration is designed to preserve existing data.
-- It adds missing columns and updates incompatible column types.
-- It does NOT drop tables or delete existing records.
-- ============================================================

SET FOREIGN_KEY_CHECKS = 0;

-- ============================================================
-- USERS
-- ============================================================

-- Add password_hash if the old database only has password.
SET @column_exists = (
    SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'users'
      AND COLUMN_NAME = 'password_hash'
);

SET @sql = IF(
    @column_exists = 0,
    'ALTER TABLE users ADD COLUMN password_hash VARCHAR(255) NULL AFTER email',
    'SELECT 1'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Copy existing password hashes into the new column.
SET @old_password_exists = (
    SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'users'
      AND COLUMN_NAME = 'password'
);

SET @sql = IF(
    @old_password_exists > 0,
    'UPDATE users SET password_hash = password WHERE (password_hash IS NULL OR password_hash = '''') AND password IS NOT NULL',
    'SELECT 1'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Make password_hash required after copying existing values.
ALTER TABLE users
    MODIFY COLUMN password_hash VARCHAR(255) NOT NULL;

-- Make legacy password column nullable if it exists.
SET @old_password_exists = (
    SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'users'
      AND COLUMN_NAME = 'password'
);

SET @sql = IF(
    @old_password_exists > 0,
    'ALTER TABLE users MODIFY COLUMN password VARCHAR(255) NULL DEFAULT NULL',
    'SELECT 1'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Add updated_at if missing.
SET @column_exists = (
    SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'users'
      AND COLUMN_NAME = 'updated_at'
);

SET @sql = IF(
    @column_exists = 0,
    'ALTER TABLE users ADD COLUMN updated_at DATETIME NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP',
    'SELECT 1'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;


-- ============================================================
-- TAILORS
-- ============================================================

-- Add updated_at if missing.
SET @column_exists = (
    SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'tailors'
      AND COLUMN_NAME = 'updated_at'
);

SET @sql = IF(
    @column_exists = 0,
    'ALTER TABLE tailors ADD COLUMN updated_at DATETIME NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP',
    'SELECT 1'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Make availability compatible with the Flask model.
ALTER TABLE tailors
    MODIFY COLUMN availability VARCHAR(50) NOT NULL DEFAULT 'available';

-- Convert old numeric availability values after changing the type.
UPDATE tailors SET availability = 'available' WHERE availability IN ('1', '');
UPDATE tailors SET availability = 'unavailable' WHERE availability = '0';


-- ============================================================
-- MEASUREMENTS
-- ============================================================

-- Add is_default if missing.
SET @column_exists = (
    SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'measurements'
      AND COLUMN_NAME = 'is_default'
);

SET @sql = IF(
    @column_exists = 0,
    'ALTER TABLE measurements ADD COLUMN is_default BOOLEAN NOT NULL DEFAULT FALSE',
    'SELECT 1'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Add updated_at if missing.
SET @column_exists = (
    SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'measurements'
      AND COLUMN_NAME = 'updated_at'
);

SET @sql = IF(
    @column_exists = 0,
    'ALTER TABLE measurements ADD COLUMN updated_at DATETIME NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP',
    'SELECT 1'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;


-- ============================================================
-- ORDERS
-- ============================================================

-- quotation_notes
SET @column_exists = (
    SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'orders'
      AND COLUMN_NAME = 'quotation_notes'
);

SET @sql = IF(
    @column_exists = 0,
    'ALTER TABLE orders ADD COLUMN quotation_notes TEXT NULL',
    'SELECT 1'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- updated_at
SET @column_exists = (
    SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'orders'
      AND COLUMN_NAME = 'updated_at'
);

SET @sql = IF(
    @column_exists = 0,
    'ALTER TABLE orders ADD COLUMN updated_at DATETIME NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP',
    'SELECT 1'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;


-- ============================================================
-- NORMALIZE OLD ORDER STATUS VALUES
-- ============================================================

UPDATE orders
SET status = 'pending'
WHERE LOWER(REPLACE(status, ' ', '_')) IN (
    'pending',
    'order_received'
);

UPDATE orders
SET status = 'quoted'
WHERE LOWER(REPLACE(status, ' ', '_')) IN (
    'quoted',
    'quote_sent'
);

UPDATE orders
SET status = 'confirmed'
WHERE LOWER(REPLACE(status, ' ', '_')) = 'confirmed';

UPDATE orders
SET status = 'cutting'
WHERE LOWER(REPLACE(status, ' ', '_')) = 'cutting';

UPDATE orders
SET status = 'stitching'
WHERE LOWER(REPLACE(status, ' ', '_')) = 'stitching';

UPDATE orders
SET status = 'alteration'
WHERE LOWER(REPLACE(status, ' ', '_')) = 'alteration';

UPDATE orders
SET status = 'quality_check'
WHERE LOWER(REPLACE(status, ' ', '_')) IN (
    'quality_check',
    'qualitycheck'
);

UPDATE orders
SET status = 'ready'
WHERE LOWER(REPLACE(status, ' ', '_')) = 'ready';

UPDATE orders
SET status = 'delivered'
WHERE LOWER(REPLACE(status, ' ', '_')) = 'delivered';

UPDATE orders
SET status = 'cancelled'
WHERE LOWER(REPLACE(status, ' ', '_')) = 'cancelled';


-- ============================================================
-- ORDER COLUMN TYPES
-- ============================================================

ALTER TABLE orders
    MODIFY COLUMN service_type VARCHAR(50) NOT NULL;

ALTER TABLE orders
    MODIFY COLUMN clothing_type VARCHAR(100) NOT NULL;

ALTER TABLE orders
    MODIFY COLUMN description TEXT NULL;

ALTER TABLE orders
    MODIFY COLUMN status VARCHAR(50) NOT NULL DEFAULT 'pending';

ALTER TABLE orders
    MODIFY COLUMN delivery_method VARCHAR(50) NOT NULL DEFAULT 'pickup';

ALTER TABLE orders
    MODIFY COLUMN quotation DECIMAL(10,2) NULL;

ALTER TABLE orders
    MODIFY COLUMN quotation_notes TEXT NULL;


-- ============================================================
-- MESSAGES
-- ============================================================

SET @column_exists = (
    SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'messages'
      AND COLUMN_NAME = 'is_read'
);

SET @sql = IF(
    @column_exists = 0,
    'ALTER TABLE messages ADD COLUMN is_read BOOLEAN NOT NULL DEFAULT FALSE',
    'SELECT 1'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;


-- ============================================================
-- REVIEWS
-- ============================================================

SET @column_exists = (
    SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'reviews'
      AND COLUMN_NAME = 'created_at'
);

SET @sql = IF(
    @column_exists = 0,
    'ALTER TABLE reviews ADD COLUMN created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP',
    'SELECT 1'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;


-- ============================================================
-- ENSURE NEW/OLD TAILOR RATINGS ARE VALID
-- ============================================================

UPDATE tailors
SET rating = 0
WHERE rating IS NULL;

UPDATE tailors
SET total_reviews = 0
WHERE total_reviews IS NULL;


-- ============================================================
-- REFRESH TAILOR RATINGS FROM REVIEWS
-- ============================================================

UPDATE tailors t
LEFT JOIN (
    SELECT
        tailor_id,
        AVG(rating) AS avg_rating,
        COUNT(*) AS review_count
    FROM reviews
    GROUP BY tailor_id
) r ON r.tailor_id = t.id
SET
    t.rating = COALESCE(r.avg_rating, 0),
    t.total_reviews = COALESCE(r.review_count, 0);


-- ============================================================
-- FINAL TIMESTAMP BACKFILL
-- ============================================================

UPDATE users
SET updated_at = COALESCE(updated_at, created_at, CURRENT_TIMESTAMP)
WHERE updated_at IS NULL;

UPDATE tailors
SET updated_at = COALESCE(updated_at, created_at, CURRENT_TIMESTAMP)
WHERE updated_at IS NULL;

UPDATE measurements
SET updated_at = COALESCE(updated_at, created_at, CURRENT_TIMESTAMP)
WHERE updated_at IS NULL;

UPDATE orders
SET updated_at = COALESCE(updated_at, created_at, CURRENT_TIMESTAMP)
WHERE updated_at IS NULL;


-- ============================================================
-- COMPLETE
-- ============================================================

SET FOREIGN_KEY_CHECKS = 1;