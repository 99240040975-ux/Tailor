-- =============================================================
--  Local Tailor Connect — Full Database Schema + Seed Data
--  Engine: MySQL 8.0+
-- =============================================================

CREATE DATABASE IF NOT EXISTS local_tailor_connect
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE local_tailor_connect;

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
    id            INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id       INT UNSIGNED NOT NULL UNIQUE,
    shop_name     VARCHAR(150) NOT NULL,
    specialization VARCHAR(200),
    address       TEXT,
    city          VARCHAR(100),
    description   TEXT,
    experience    INT UNSIGNED DEFAULT 0,
    price_range   VARCHAR(50),
    availability  TINYINT(1)  NOT NULL DEFAULT 1,
    rating        DECIMAL(3,2) NOT NULL DEFAULT 0.00,
    total_reviews INT UNSIGNED NOT NULL DEFAULT 0,
    is_verified   TINYINT(1)  NOT NULL DEFAULT 0,
    created_at    DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_tailors_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_tailors_city (city),
    INDEX idx_tailors_rating (rating DESC),
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

-- -----------------------------------------------------------
-- SEED DATA (passwords are bcrypt of "password123")
-- -----------------------------------------------------------
INSERT INTO users (name, email, password, phone, role) VALUES
('Admin User',       'admin@tailor.com',   'pbkdf2:sha256:600000$seed$admin_hash_placeholder',   '9000000001', 'admin'),
('Arjun Kumar',      'arjun@example.com',  'pbkdf2:sha256:600000$seed$customer_hash_placeholder', '9000000002', 'customer'),
('Priya Sharma',     'priya@example.com',  'pbkdf2:sha256:600000$seed$customer_hash_placeholder', '9000000003', 'customer'),
('Ravi Tailors',     'ravi@tailor.com',    'pbkdf2:sha256:600000$seed$tailor_hash_placeholder',   '9000000004', 'tailor'),
('Meena Creations',  'meena@tailor.com',   'pbkdf2:sha256:600000$seed$tailor_hash_placeholder',   '9000000005', 'tailor');

INSERT INTO tailors (user_id, shop_name, specialization, address, city, description, experience, price_range, availability, rating, total_reviews, is_verified) VALUES
(4, 'Ravi Master Tailors',  'Mens Suits, Sherwanis, Kurtas',    '12, MG Road', 'Bangalore', 'Expert in ethnic and formal wear with 15 years experience.', 15, '₹500 - ₹5000',  1, 4.70, 34, 1),
(5, 'Meena Fashion Studio', 'Ladies Suits, Blouses, Alterations','7, Anna Nagar', 'Chennai', 'Specializing in ladies wear and designer blouses.', 10, '₹300 - ₹3000', 1, 4.50, 28, 1);
