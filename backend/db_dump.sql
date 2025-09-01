-- MariaDB/MySQL schema for Futura Intranet v001
CREATE DATABASE IF NOT EXISTS `intranet_futura` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `intranet_futura `;

CREATE TABLE IF NOT EXISTS roles (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(50) UNIQUE NOT NULL,
  description VARCHAR(255) DEFAULT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS users (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  email VARCHAR(255) UNIQUE NOT NULL,
  username VARCHAR(100) UNIQUE NOT NULL,
  full_name VARCHAR(255) DEFAULT NULL,
  hashed_password VARCHAR(255) NOT NULL,
  phone VARCHAR(50) DEFAULT NULL,
  is_active TINYINT(1) DEFAULT 1,
  profile_complete TINYINT(1) DEFAULT 0,
  role_id BIGINT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (role_id) REFERENCES roles(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS user_profiles (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id BIGINT NOT NULL,
  emergency_contact_name VARCHAR(255),
  emergency_contact_phone VARCHAR(50),
  address_line VARCHAR(255),
  city VARCHAR(255),
  country VARCHAR(255),
  skills TEXT,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS offices (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(255) UNIQUE NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS contracts (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  office_id BIGINT NOT NULL,
  code VARCHAR(50) UNIQUE NOT NULL,
  name VARCHAR(255) NOT NULL,
  client_type ENUM('external','internal') NOT NULL,
  status ENUM('active','on_hold','to_be_liquidated','archived') NOT NULL DEFAULT 'active',
  created_by BIGINT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  description TEXT,
  FOREIGN KEY (office_id) REFERENCES offices(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS user_favorites (
  user_id BIGINT NOT NULL,
  contract_id BIGINT NOT NULL,
  PRIMARY KEY (user_id, contract_id),
  FOREIGN KEY (contract_id) REFERENCES contracts(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS contract_access (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  contract_id BIGINT NOT NULL,
  user_id BIGINT NOT NULL,
  role VARCHAR(50) DEFAULT 'member',
  UNIQUE KEY uq_access (contract_id, user_id),
  FOREIGN KEY (contract_id) REFERENCES contracts(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS contract_client_tokens (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  contract_id BIGINT NOT NULL,
  token VARCHAR(64) UNIQUE NOT NULL,
  is_enabled TINYINT(1) NOT NULL DEFAULT 1,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (contract_id) REFERENCES contracts(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS leave_requests (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id BIGINT NOT NULL,
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  leave_type VARCHAR(50) NOT NULL,
  reason TEXT,
  status VARCHAR(20) NOT NULL DEFAULT 'pending',
  approver_id BIGINT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS timesheets (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id BIGINT NOT NULL,
  contract_id BIGINT NULL,
  work_date DATE NOT NULL,
  hours_worked DECIMAL(5,2) NOT NULL,
  description TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS budgets (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  contract_id BIGINT NOT NULL,
  amount DECIMAL(14,2) NOT NULL,
  currency VARCHAR(8) NOT NULL DEFAULT 'USD',
  approved TINYINT(1) DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS invoices (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  contract_id BIGINT NOT NULL,
  amount DECIMAL(14,2) NOT NULL,
  currency VARCHAR(8) NOT NULL DEFAULT 'USD',
  issued_date DATE NOT NULL,
  status ENUM('draft','sent','paid','overdue') NOT NULL DEFAULT 'draft',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS qa_checklists (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  contract_id BIGINT NOT NULL,
  title VARCHAR(255) NOT NULL,
  status ENUM('open','closed') NOT NULL DEFAULT 'open',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS safety_reports (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  contract_id BIGINT NOT NULL,
  report_date DATE NOT NULL,
  notes TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS environment_reports (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  contract_id BIGINT NOT NULL,
  report_date DATE NOT NULL,
  notes TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS helpdesk_tickets (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  created_by BIGINT NOT NULL,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  priority ENUM('low','normal','high','urgent') NOT NULL DEFAULT 'normal',
  status ENUM('open','in_progress','resolved','closed') NOT NULL DEFAULT 'open',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS clients (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255),
  phone VARCHAR(100)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS file_shares (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  owner_id BIGINT NOT NULL,
  original_name VARCHAR(255) NOT NULL,
  stored_name VARCHAR(255) NOT NULL,
  stored_path VARCHAR(500) NOT NULL,
  size_bytes BIGINT NOT NULL,
  mime_type VARCHAR(100),
  token VARCHAR(64) UNIQUE NOT NULL,
  downloads INT NOT NULL DEFAULT 0,
  last_download_at DATETIME NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS file_download_logs (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  file_id BIGINT NOT NULL,
  ip_address VARCHAR(45) NOT NULL,
  downloaded_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS library_categories (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(255) NOT NULL,
  description VARCHAR(255)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS library_items (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  category_id BIGINT NULL,
  title VARCHAR(255) NOT NULL,
  path VARCHAR(500) NOT NULL,
  uploaded_by BIGINT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

INSERT IGNORE INTO roles (id, name, description) VALUES
  (1,'admin','System administrator'),
  (2,'manager','Department/Project manager'),
  (3,'user','Standard user');

INSERT IGNORE INTO offices (id, name) VALUES (1,'Phnom Penh'), (2,'Ho Chi Minh City'), (3,'Bangkok'), (4,'Hanoi');
