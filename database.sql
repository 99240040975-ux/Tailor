-- =============================================================
--  Local Tailor Connect — Full Database Schema + Location Hierarchy
--  Engine: MySQL 8.0+
-- =============================================================

CREATE DATABASE IF NOT EXISTS local_tailor_connect
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE local_tailor_connect;

-- -----------------------------------------------------------
-- 1. STATES
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS states (
    id         INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(100) NOT NULL UNIQUE,
    code       VARCHAR(10),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_states_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------
-- 2. DISTRICTS
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS districts (
    id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    state_id    INT UNSIGNED NOT NULL,
    name        VARCHAR(100) NOT NULL,
    code        VARCHAR(20),
    census_code VARCHAR(20),
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_districts_state FOREIGN KEY (state_id) REFERENCES states(id) ON DELETE CASCADE,
    INDEX idx_districts_state (state_id),
    INDEX idx_districts_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------
-- 3. TALUKS
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS taluks (
    id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    district_id INT UNSIGNED NOT NULL,
    name        VARCHAR(120) NOT NULL,
    code        VARCHAR(20),
    census_code VARCHAR(20),
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_taluks_district FOREIGN KEY (district_id) REFERENCES districts(id) ON DELETE CASCADE,
    INDEX idx_taluks_district (district_id),
    INDEX idx_taluks_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------
-- 4. CITIES
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS cities (
    id             INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    district_id    INT UNSIGNED NOT NULL,
    taluk_id       INT UNSIGNED,
    name           VARCHAR(150) NOT NULL,
    code           VARCHAR(20),
    localbody_type VARCHAR(50),
    created_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_cities_district FOREIGN KEY (district_id) REFERENCES districts(id) ON DELETE CASCADE,
    CONSTRAINT fk_cities_taluk    FOREIGN KEY (taluk_id) REFERENCES taluks(id) ON DELETE SET NULL,
    INDEX idx_cities_district (district_id),
    INDEX idx_cities_taluk (taluk_id),
    INDEX idx_cities_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------
-- 5. TOWNS
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS towns (
    id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    district_id INT UNSIGNED NOT NULL,
    taluk_id    INT UNSIGNED,
    city_id     INT UNSIGNED,
    name        VARCHAR(150) NOT NULL,
    code        VARCHAR(20),
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_towns_district FOREIGN KEY (district_id) REFERENCES districts(id) ON DELETE CASCADE,
    CONSTRAINT fk_towns_taluk    FOREIGN KEY (taluk_id) REFERENCES taluks(id) ON DELETE SET NULL,
    CONSTRAINT fk_towns_city     FOREIGN KEY (city_id) REFERENCES cities(id) ON DELETE SET NULL,
    INDEX idx_towns_district (district_id),
    INDEX idx_towns_taluk (taluk_id),
    INDEX idx_towns_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------
-- 6. VILLAGES
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS villages (
    id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    district_id INT UNSIGNED NOT NULL,
    taluk_id    INT UNSIGNED NOT NULL,
    town_id     INT UNSIGNED,
    name        VARCHAR(150) NOT NULL,
    code        VARCHAR(20),
    census_code VARCHAR(20),
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_villages_district FOREIGN KEY (district_id) REFERENCES districts(id) ON DELETE CASCADE,
    CONSTRAINT fk_villages_taluk    FOREIGN KEY (taluk_id) REFERENCES taluks(id) ON DELETE CASCADE,
    CONSTRAINT fk_villages_town     FOREIGN KEY (town_id) REFERENCES towns(id) ON DELETE SET NULL,
    INDEX idx_villages_district (district_id),
    INDEX idx_villages_taluk (taluk_id),
    INDEX idx_villages_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------
-- 7. LOCALITIES
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS localities (
    id         INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    city_id    INT UNSIGNED,
    town_id    INT UNSIGNED,
    village_id INT UNSIGNED,
    name       VARCHAR(150) NOT NULL,
    pincode    VARCHAR(10),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_localities_city    FOREIGN KEY (city_id) REFERENCES cities(id) ON DELETE SET NULL,
    CONSTRAINT fk_localities_town    FOREIGN KEY (town_id) REFERENCES towns(id) ON DELETE SET NULL,
    CONSTRAINT fk_localities_village FOREIGN KEY (village_id) REFERENCES villages(id) ON DELETE SET NULL,
    INDEX idx_localities_name (name),
    INDEX idx_localities_pincode (pincode)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------
-- USERS
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(120)  NOT NULL,
    email       VARCHAR(180)  NOT NULL UNIQUE,
    password    VARCHAR(256)  NOT NULL,
    phone       VARCHAR(20),
    role        ENUM('customer','tailor','admin') NOT NULL DEFAULT 'customer',
    profile_pic VARCHAR(255),
    is_active   TINYINT(1)    NOT NULL DEFAULT 1,
    created_at  DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_users_role (role),
    INDEX idx_users_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------
-- TAILORS
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS tailors (
    id             INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id        INT UNSIGNED NOT NULL UNIQUE,
    shop_name      VARCHAR(150) NOT NULL,
    specialization VARCHAR(200),
    address        TEXT,
    city           VARCHAR(100),
    description    TEXT,
    experience     INT UNSIGNED DEFAULT 0,
    price_range    VARCHAR(50),
    availability   TINYINT(1)  NOT NULL DEFAULT 1,
    rating         DECIMAL(3,2) NOT NULL DEFAULT 0.00,
    total_reviews  INT UNSIGNED NOT NULL DEFAULT 0,
    
    -- Hierarchical Location references
    state_id       INT UNSIGNED,
    district_id    INT UNSIGNED,
    taluk_id       INT UNSIGNED,
    city_id        INT UNSIGNED,
    town_id        INT UNSIGNED,
    village_id     INT UNSIGNED,
    
    latitude       DECIMAL(10,8),
    longitude      DECIMAL(11,8),
    is_verified    TINYINT(1)  NOT NULL DEFAULT 0,
    is_active      TINYINT(1)  NOT NULL DEFAULT 1,
    created_at     DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_tailors_user     FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_tailors_state    FOREIGN KEY (state_id) REFERENCES states(id) ON DELETE SET NULL,
    CONSTRAINT fk_tailors_district FOREIGN KEY (district_id) REFERENCES districts(id) ON DELETE SET NULL,
    CONSTRAINT fk_tailors_taluk    FOREIGN KEY (taluk_id) REFERENCES taluks(id) ON DELETE SET NULL,
    CONSTRAINT fk_tailors_city     FOREIGN KEY (city_id) REFERENCES cities(id) ON DELETE SET NULL,
    CONSTRAINT fk_tailors_town     FOREIGN KEY (town_id) REFERENCES towns(id) ON DELETE SET NULL,
    CONSTRAINT fk_tailors_village  FOREIGN KEY (village_id) REFERENCES villages(id) ON DELETE SET NULL,
    
    INDEX idx_tailors_city (city),
    INDEX idx_tailors_district (district_id),
    INDEX idx_tailors_taluk (taluk_id),
    INDEX idx_tailors_rating (rating DESC),
    INDEX idx_tailors_is_active (is_active),
    INDEX idx_tailors_availability (availability)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------
-- MEASUREMENTS
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS measurements (
    id           INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    customer_id  INT UNSIGNED NOT NULL,
    profile_name VARCHAR(100) NOT NULL,
    chest        DECIMAL(5,2),
    waist        DECIMAL(5,2),
    hip          DECIMAL(5,2),
    shoulder     DECIMAL(5,2),
    sleeve       DECIMAL(5,2),
    neck         DECIMAL(5,2),
    inseam       DECIMAL(5,2),
    height       DECIMAL(5,2),
    unit         ENUM('inches','cm') NOT NULL DEFAULT 'inches',
    notes        TEXT,
    created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_meas_customer FOREIGN KEY (customer_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_meas_customer (customer_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------
-- ORDERS
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS orders (
    id               INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    customer_id      INT UNSIGNED NOT NULL,
    tailor_id        INT UNSIGNED NOT NULL,
    measurement_id   INT UNSIGNED,
    service_type     ENUM('custom','alteration','repair','embroidery','other') NOT NULL,
    clothing_type    VARCHAR(100),
    description      TEXT,
    reference_image  VARCHAR(255),
    quotation        DECIMAL(10,2),
    quotation_notes  TEXT,
    status           ENUM('pending','quoted','confirmed','cutting','stitching',
                          'alteration','quality_check','ready','delivered','cancelled')
                     NOT NULL DEFAULT 'pending',
    delivery_method  ENUM('pickup','delivery') NOT NULL DEFAULT 'pickup',
    delivery_address TEXT,
    expected_date    DATE,
    created_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_orders_customer    FOREIGN KEY (customer_id)    REFERENCES users(id)         ON DELETE RESTRICT,
    CONSTRAINT fk_orders_tailor      FOREIGN KEY (tailor_id)      REFERENCES tailors(id)        ON DELETE RESTRICT,
    CONSTRAINT fk_orders_measurement FOREIGN KEY (measurement_id) REFERENCES measurements(id)   ON DELETE SET NULL,
    INDEX idx_orders_customer (customer_id),
    INDEX idx_orders_tailor   (tailor_id),
    INDEX idx_orders_status   (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------
-- MESSAGES
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS messages (
    id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    sender_id   INT UNSIGNED NOT NULL,
    receiver_id INT UNSIGNED NOT NULL,
    order_id    INT UNSIGNED,
    message     TEXT NOT NULL,
    is_read     TINYINT(1) NOT NULL DEFAULT 0,
    created_at  DATETIME   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_msg_sender   FOREIGN KEY (sender_id)   REFERENCES users(id)  ON DELETE CASCADE,
    CONSTRAINT fk_msg_receiver FOREIGN KEY (receiver_id) REFERENCES users(id)  ON DELETE CASCADE,
    CONSTRAINT fk_msg_order    FOREIGN KEY (order_id)    REFERENCES orders(id) ON DELETE SET NULL,
    INDEX idx_msg_receiver (receiver_id),
    INDEX idx_msg_order    (order_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------
-- REVIEWS
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS reviews (
    id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    customer_id INT UNSIGNED NOT NULL,
    tailor_id   INT UNSIGNED NOT NULL,
    order_id    INT UNSIGNED NOT NULL UNIQUE,
    rating      TINYINT UNSIGNED NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment     TEXT,
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_rev_customer FOREIGN KEY (customer_id) REFERENCES users(id)    ON DELETE CASCADE,
    CONSTRAINT fk_rev_tailor   FOREIGN KEY (tailor_id)   REFERENCES tailors(id)  ON DELETE CASCADE,
    CONSTRAINT fk_rev_order    FOREIGN KEY (order_id)    REFERENCES orders(id)   ON DELETE CASCADE,
    INDEX idx_rev_tailor (tailor_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
