-- ============================================================================
-- CCMC Hamilton 教会管理系统 Database Schema
-- 汉美顿怀恩堂 (Hamilton Chinese Methodist Church) Management System
-- MySQL 5.7+ / 8.0+
-- ============================================================================

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS attendance;
DROP TABLE IF EXISTS rosters;
DROP TABLE IF EXISTS visitors;
DROP TABLE IF EXISTS prayer_requests;
DROP TABLE IF EXISTS announcements;
DROP TABLE IF EXISTS events;
DROP TABLE IF EXISTS resources;
DROP TABLE IF EXISTS group_membership;
DROP TABLE IF EXISTS `groups`;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS roles;
DROP TABLE IF EXISTS church_settings;

SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================================
-- 角色 (Roles)
-- 1 系统管理员 Super Admin | 2 执事 Coordinator | 3 服事人员 Operator | 4 会友 Member
-- ============================================================================
CREATE TABLE roles (
    role_id INT AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL UNIQUE,
    role_name_en VARCHAR(50) NULL
) ENGINE=InnoDB;

-- ============================================================================
-- 用户 (Members / Users)
-- ============================================================================
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    phone VARCHAR(50),
    email VARCHAR(255) UNIQUE,
    emergency_contact VARCHAR(100),
    password_hash VARCHAR(255) NOT NULL,
    role_id INT NOT NULL DEFAULT 4,
    status ENUM('Active', 'Inactive', 'Suspended') DEFAULT 'Active',
    profile_photo VARCHAR(255),
    preferred_language VARCHAR(20) DEFAULT 'zh',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(role_id)
) ENGINE=InnoDB;

-- ============================================================================
-- 团契 / 事工小组 (Fellowships & Ministries)
-- ============================================================================
CREATE TABLE `groups` (
    group_id INT AUTO_INCREMENT PRIMARY KEY,
    group_name VARCHAR(80) UNIQUE NOT NULL,
    group_name_en VARCHAR(255) NULL,
    group_type ENUM('fellowship', 'ministry', 'worship') NOT NULL DEFAULT 'fellowship',
    description TEXT,
    description_en TEXT NULL,
    meeting_time VARCHAR(100),
    meeting_time_en VARCHAR(100) NULL,
    meeting_location VARCHAR(200),
    meeting_location_en VARCHAR(200) NULL,
    contact_phone VARCHAR(50),
    leader_user_id INT NULL,
    visibility ENUM('public', 'private') NOT NULL DEFAULT 'public',
    status ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
    primary_color VARCHAR(7) DEFAULT '#1f3a2d',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INT NULL,
    FOREIGN KEY (leader_user_id) REFERENCES users(user_id),
    FOREIGN KEY (created_by) REFERENCES users(user_id)
) ENGINE=InnoDB;

CREATE TABLE group_membership (
    membership_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    group_id INT NOT NULL,
    is_leader TINYINT(1) NOT NULL DEFAULT 0,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    membership_status VARCHAR(20) NOT NULL DEFAULT 'active',
    UNIQUE (user_id, group_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES `groups`(group_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================================
-- 行事历 / 活动 (Events)
-- ============================================================================
CREATE TABLE events (
    event_id INT AUTO_INCREMENT PRIMARY KEY,
    group_id INT NULL,
    title VARCHAR(150) NOT NULL,
    title_en VARCHAR(255) NULL,
    description TEXT,
    description_en TEXT NULL,
    location VARCHAR(200),
    location_en VARCHAR(200) NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME NULL,
    category ENUM('worship', 'prayer', 'fellowship', 'outreach', 'ministry', 'special', 'other') NOT NULL DEFAULT 'other',
    cover_image VARCHAR(255),
    is_published TINYINT(1) NOT NULL DEFAULT 0,
    created_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    KEY idx_events_start (start_time),
    FOREIGN KEY (group_id) REFERENCES `groups`(group_id) ON DELETE SET NULL,
    FOREIGN KEY (created_by) REFERENCES users(user_id)
) ENGINE=InnoDB;

-- ============================================================================
-- 活动宣传 / 教会通知 (Announcements)
-- ============================================================================
CREATE TABLE announcements (
    announcement_id INT AUTO_INCREMENT PRIMARY KEY,
    group_id INT NULL,
    title VARCHAR(150) NOT NULL,
    title_en VARCHAR(255) NULL,
    content TEXT,
    content_en TEXT NULL,
    image_url VARCHAR(255),
    is_published TINYINT(1) NOT NULL DEFAULT 1,
    created_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES `groups`(group_id) ON DELETE SET NULL,
    FOREIGN KEY (created_by) REFERENCES users(user_id)
) ENGINE=InnoDB;

-- ============================================================================
-- 代祷事项 (Prayer Requests)
-- ============================================================================
CREATE TABLE prayer_requests (
    request_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    title_en VARCHAR(255) NULL,
    content TEXT NOT NULL,
    content_en TEXT NULL,
    is_public TINYINT(1) NOT NULL DEFAULT 0,
    status ENUM('pending', 'praying', 'answered') NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================================
-- 新朋友 (Visitors)
-- ============================================================================
CREATE TABLE visitors (
    visitor_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) DEFAULT '',
    email VARCHAR(255),
    phone VARCHAR(50),
    fellowship_interest VARCHAR(100),
    heard_from VARCHAR(100),
    notes TEXT,
    status ENUM('new', 'contacted', 'joined', 'declined') NOT NULL DEFAULT 'new',
    created_by INT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    KEY idx_visitors_created (created_at),
    FOREIGN KEY (created_by) REFERENCES users(user_id)
) ENGINE=InnoDB;

-- ============================================================================
-- 崇拜 / 活动出席记录 (Attendance)
-- ============================================================================
CREATE TABLE attendance (
    attendance_id INT AUTO_INCREMENT PRIMARY KEY,
    event_id INT NULL,
    service_date DATE NOT NULL,
    attendee_name VARCHAR(100) NOT NULL,
    user_id INT NULL,
    recorded_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    KEY idx_attendance_date (service_date),
    FOREIGN KEY (event_id) REFERENCES events(event_id) ON DELETE SET NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL,
    FOREIGN KEY (recorded_by) REFERENCES users(user_id)
) ENGINE=InnoDB;

-- ============================================================================
-- 服事轮值 (Rosters)
-- ============================================================================
CREATE TABLE rosters (
    roster_id INT AUTO_INCREMENT PRIMARY KEY,
    group_id INT NULL,
    event_id INT NULL,
    task_name VARCHAR(80) NOT NULL,
    service_date DATE NOT NULL,
    user_id INT NOT NULL,
    status ENUM('pending', 'confirmed', 'completed') NOT NULL DEFAULT 'pending',
    notes VARCHAR(255),
    created_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    KEY idx_rosters_date (service_date),
    FOREIGN KEY (group_id) REFERENCES `groups`(group_id) ON DELETE SET NULL,
    FOREIGN KEY (event_id) REFERENCES events(event_id) ON DELETE SET NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(user_id)
) ENGINE=InnoDB;

-- ============================================================================
-- 资源库：诗歌 / 经文 / 见证 / 资料 (Resources)
-- ============================================================================
CREATE TABLE resources (
    resource_id INT AUTO_INCREMENT PRIMARY KEY,
    category VARCHAR(50) NOT NULL DEFAULT '资料',
    title VARCHAR(150) NOT NULL,
    title_en VARCHAR(255) NULL,
    content TEXT,
    content_en TEXT NULL,
    photo_url VARCHAR(255),
    is_featured TINYINT(1) NOT NULL DEFAULT 0,
    is_published TINYINT(1) NOT NULL DEFAULT 0,
    created_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(user_id)
) ENGINE=InnoDB;

-- ============================================================================
-- 教会设置 (Church Settings)
-- ============================================================================
CREATE TABLE church_settings (
    setting_key VARCHAR(60) PRIMARY KEY,
    setting_value TEXT
) ENGINE=InnoDB;

