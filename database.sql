-- =============================================================
-- TailorConnect
-- Complete MySQL 8.0+ Database Schema
-- =============================================================

CREATE DATABASE IF NOT EXISTS local_tailor_connect
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE local_tailor_connect;


-- =============================================================
-- 1. STATES
-- =============================================================

CREATE TABLE IF NOT EXISTS states (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    code VARCHAR(10),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_states_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- =============================================================
-- 2. DISTRICTS
-- =============================================================

CREATE TABLE IF NOT EXISTS districts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    state_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(20),
    census_code VARCHAR(20),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_districts_state
        FOREIGN KEY (state_id)
        REFERENCES states(id)
        ON DELETE CASCADE,

    INDEX idx_districts_state (state_id),
    INDEX idx_districts_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- =============================================================
-- 3. TALUKS
-- =============================================================

CREATE TABLE IF NOT EXISTS taluks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    district_id INT NOT NULL,
    name VARCHAR(120) NOT NULL,
    code VARCHAR(20),
    census_code VARCHAR(20),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_taluks_district
        FOREIGN KEY (district_id)
        REFERENCES districts(id)
        ON DELETE CASCADE,

    INDEX idx_taluks_district (district_id),
    INDEX idx_taluks_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- =============================================================
-- 4. CITIES
-- =============================================================

CREATE TABLE IF NOT EXISTS cities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    district_id INT NOT NULL,
    taluk_id INT NULL,
    name VARCHAR(150) NOT NULL,
    code VARCHAR(20),
    localbody_type VARCHAR(50),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_cities_district
        FOREIGN KEY (district_id)
        REFERENCES districts(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_cities_taluk
        FOREIGN KEY (taluk_id)
        REFERENCES taluks(id)
        ON DELETE SET NULL,

    INDEX idx_cities_district (district_id),
    INDEX idx_cities_taluk (taluk_id),
    INDEX idx_cities_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- =============================================================
-- 5. TOWNS
-- =============================================================

CREATE TABLE IF NOT EXISTS towns (
    id INT AUTO_INCREMENT PRIMARY KEY,
    district_id INT NOT NULL,
    taluk_id INT NULL,
    city_id INT NULL,
    name VARCHAR(150) NOT NULL,
    code VARCHAR(20),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_towns_district
        FOREIGN KEY (district_id)
        REFERENCES districts(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_towns_taluk
        FOREIGN KEY (taluk_id)
        REFERENCES taluks(id)
        ON DELETE SET NULL,

    CONSTRAINT fk_towns_city
        FOREIGN KEY (city_id)
        REFERENCES cities(id)
        ON DELETE SET NULL,

    INDEX idx_towns_district (district_id),
    INDEX idx_towns_taluk (taluk_id),
    INDEX idx_towns_city (city_id),
    INDEX idx_towns_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- =============================================================
-- 6. VILLAGES
-- =============================================================

CREATE TABLE IF NOT EXISTS villages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    district_id INT NOT NULL,
    taluk_id INT NOT NULL,
    town_id INT NULL,
    name VARCHAR(150) NOT NULL,
    code VARCHAR(20),
    census_code VARCHAR(20),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_villages_district
        FOREIGN KEY (district_id)
        REFERENCES districts(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_villages_taluk
        FOREIGN KEY (taluk_id)
        REFERENCES taluks(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_villages_town
        FOREIGN KEY (town_id)
        REFERENCES towns(id)
        ON DELETE SET NULL,

    INDEX idx_villages_district (district_id),
    INDEX idx_villages_taluk (taluk_id),
    INDEX idx_villages_town (town_id),
    INDEX idx_villages_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- =============================================================
-- 7. LOCALITIES
-- =============================================================

CREATE TABLE IF NOT EXISTS localities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    city_id INT NULL,
    town_id INT NULL,
    village_id INT NULL,
    name VARCHAR(150) NOT NULL,
    pincode VARCHAR(10),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_localities_city
        FOREIGN KEY (city_id)
        REFERENCES cities(id)
        ON DELETE SET NULL,

    CONSTRAINT fk_localities_town
        FOREIGN KEY (town_id)
        REFERENCES towns(id)
        ON DELETE SET NULL,

    CONSTRAINT fk_localities_village
        FOREIGN KEY (village_id)
        REFERENCES villages(id)
        ON DELETE SET NULL,

    INDEX idx_localities_city (city_id),
    INDEX idx_localities_town (town_id),
    INDEX idx_localities_village (village_id),
    INDEX idx_localities_name (name),
    INDEX idx_localities_pincode (pincode)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- =============================================================
-- 8. USERS
-- =============================================================

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,

    name VARCHAR(120) NOT NULL,

    email VARCHAR(180) NOT NULL UNIQUE,

    password_hash VARCHAR(255) NOT NULL,

    role ENUM(
        'customer',
        'tailor',
        'admin'
    ) NOT NULL DEFAULT 'customer',

    phone VARCHAR(20),

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_users_role (role),
    INDEX idx_users_email (email),
    INDEX idx_users_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- =============================================================
-- 9. TAILORS
-- =============================================================

CREATE TABLE IF NOT EXISTS tailors (
    id INT AUTO_INCREMENT PRIMARY KEY,

    user_id INT NOT NULL UNIQUE,

    shop_name VARCHAR(150) NOT NULL,

    specialization VARCHAR(200),

    address TEXT,

    city VARCHAR(100),

    description TEXT,

    experience INT NOT NULL DEFAULT 0,

    price_range VARCHAR(50),

    availability VARCHAR(50) NOT NULL DEFAULT 'available',

    rating DECIMAL(3,2) NOT NULL DEFAULT 0.00,

    total_reviews INT NOT NULL DEFAULT 0,

    is_verified BOOLEAN NOT NULL DEFAULT FALSE,

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    state_id INT NULL,
    district_id INT NULL,
    taluk_id INT NULL,
    city_id INT NULL,
    town_id INT NULL,
    village_id INT NULL,
    latitude DECIMAL(10, 6) NULL,
    longitude DECIMAL(10, 6) NULL,

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_tailors_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_tailors_state
        FOREIGN KEY (state_id)
        REFERENCES states(id)
        ON DELETE SET NULL,

    CONSTRAINT fk_tailors_district
        FOREIGN KEY (district_id)
        REFERENCES districts(id)
        ON DELETE SET NULL,

    CONSTRAINT fk_tailors_taluk
        FOREIGN KEY (taluk_id)
        REFERENCES taluks(id)
        ON DELETE SET NULL,

    CONSTRAINT fk_tailors_city
        FOREIGN KEY (city_id)
        REFERENCES cities(id)
        ON DELETE SET NULL,

    CONSTRAINT fk_tailors_town
        FOREIGN KEY (town_id)
        REFERENCES towns(id)
        ON DELETE SET NULL,

    CONSTRAINT fk_tailors_village
        FOREIGN KEY (village_id)
        REFERENCES villages(id)
        ON DELETE SET NULL,

    INDEX idx_tailors_city (city),
    INDEX idx_tailors_district (district_id),
    INDEX idx_tailors_taluk (taluk_id),
    INDEX idx_tailors_rating (rating),
    INDEX idx_tailors_reviews (total_reviews),
    INDEX idx_tailors_verified (is_verified),
    INDEX idx_tailors_active (is_active),
    INDEX idx_tailors_availability (availability)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- =============================================================
-- 10. MEASUREMENTS
-- =============================================================

CREATE TABLE IF NOT EXISTS measurements (
    id INT AUTO_INCREMENT PRIMARY KEY,

    customer_id INT NOT NULL,

    profile_name VARCHAR(100) NOT NULL,

    chest DECIMAL(6,2),
    waist DECIMAL(6,2),
    hip DECIMAL(6,2),
    shoulder DECIMAL(6,2),
    sleeve DECIMAL(6,2),
    neck DECIMAL(6,2),
    inseam DECIMAL(6,2),
    height DECIMAL(6,2),

    unit ENUM(
        'inches',
        'cm'
    ) NOT NULL DEFAULT 'inches',

    notes TEXT,

    is_default BOOLEAN NOT NULL DEFAULT FALSE,

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_measurements_customer
        FOREIGN KEY (customer_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    INDEX idx_measurements_customer (customer_id),
    INDEX idx_measurements_default (customer_id, is_default)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- =============================================================
-- 11. ORDERS
-- =============================================================

CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,

    customer_id INT NOT NULL,

    tailor_id INT NOT NULL,

    measurement_id INT NULL,

    service_type VARCHAR(50) NOT NULL,

    clothing_type VARCHAR(100),

    description TEXT,

    reference_image VARCHAR(255),

    quotation DECIMAL(10,2),

    quotation_notes TEXT,

    status VARCHAR(50) NOT NULL DEFAULT 'pending',

    delivery_method VARCHAR(50) NOT NULL DEFAULT 'pickup',

    delivery_address TEXT,

    expected_date DATE,

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_orders_customer
        FOREIGN KEY (customer_id)
        REFERENCES users(id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_orders_tailor
        FOREIGN KEY (tailor_id)
        REFERENCES tailors(id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_orders_measurement
        FOREIGN KEY (measurement_id)
        REFERENCES measurements(id)
        ON DELETE SET NULL,

    INDEX idx_orders_customer (customer_id),
    INDEX idx_orders_tailor (tailor_id),
    INDEX idx_orders_measurement (measurement_id),
    INDEX idx_orders_status (status),
    INDEX idx_orders_created (created_at),
    INDEX idx_orders_expected_date (expected_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- =============================================================
-- 12. MESSAGES
-- =============================================================

CREATE TABLE IF NOT EXISTS messages (
    id INT AUTO_INCREMENT PRIMARY KEY,

    sender_id INT NOT NULL,

    receiver_id INT NOT NULL,

    order_id INT NULL,

    message TEXT NOT NULL,

    is_read BOOLEAN NOT NULL DEFAULT FALSE,

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_messages_sender
        FOREIGN KEY (sender_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_messages_receiver
        FOREIGN KEY (receiver_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_messages_order
        FOREIGN KEY (order_id)
        REFERENCES orders(id)
        ON DELETE SET NULL,

    INDEX idx_messages_sender (sender_id),
    INDEX idx_messages_receiver (receiver_id),
    INDEX idx_messages_order (order_id),
    INDEX idx_messages_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- =============================================================
-- 13. REVIEWS
-- =============================================================

CREATE TABLE IF NOT EXISTS reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,

    customer_id INT NOT NULL,

    tailor_id INT NOT NULL,

    order_id INT NOT NULL UNIQUE,

    rating INT NOT NULL,

    comment TEXT,

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_reviews_rating
        CHECK (rating >= 1 AND rating <= 5),

    CONSTRAINT fk_reviews_customer
        FOREIGN KEY (customer_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_reviews_tailor
        FOREIGN KEY (tailor_id)
        REFERENCES tailors(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_reviews_order
        FOREIGN KEY (order_id)
        REFERENCES orders(id)
        ON DELETE CASCADE,

    INDEX idx_reviews_customer (customer_id),
    INDEX idx_reviews_tailor (tailor_id),
    INDEX idx_reviews_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- =============================================================
-- END OF CORE SCHEMA
-- =============================================================