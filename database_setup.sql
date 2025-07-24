-- DockFlask Database Creation Script
-- Run this in MySQL Workbench

-- Create Database
CREATE DATABASE IF NOT EXISTS dockflask_db 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- Use the database
USE dockflask_db;

-- Create Users Table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(128) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    
    -- Indexes
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_active (is_active),
    INDEX idx_admin (is_admin),
    INDEX idx_created_at (created_at)
);

-- Create Posts Table
CREATE TABLE posts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_published BOOLEAN DEFAULT TRUE,
    views INT DEFAULT 0,
    user_id INT NOT NULL,
    
    -- Foreign Key
    CONSTRAINT fk_posts_user_id 
        FOREIGN KEY (user_id) REFERENCES users(id) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    
    -- Indexes
    INDEX idx_title (title),
    INDEX idx_published (is_published),
    INDEX idx_created_at (created_at),
    INDEX idx_views (views),
    INDEX idx_user_id (user_id)
);

-- Create System Logs Table
CREATE TABLE system_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    action VARCHAR(100) NOT NULL,
    user_id INT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    details TEXT,
    
    -- Foreign Key
    CONSTRAINT fk_system_logs_user_id 
        FOREIGN KEY (user_id) REFERENCES users(id) 
        ON DELETE SET NULL ON UPDATE CASCADE,
    
    -- Indexes
    INDEX idx_action (action),
    INDEX idx_timestamp (timestamp),
    INDEX idx_user_id (user_id),
    INDEX idx_ip_address (ip_address)
);

-- Create Categories Table (for future blog categorization)
CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    slug VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_name (name),
    INDEX idx_slug (slug)
);

-- Create Post Categories Junction Table (Many-to-Many relationship)
CREATE TABLE post_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    post_id INT NOT NULL,
    category_id INT NOT NULL,
    
    -- Foreign Keys
    CONSTRAINT fk_post_categories_post_id 
        FOREIGN KEY (post_id) REFERENCES posts(id) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_post_categories_category_id 
        FOREIGN KEY (category_id) REFERENCES categories(id) 
        ON DELETE CASCADE ON UPDATE CASCADE,
        
    -- Unique constraint to prevent duplicate relationships
    UNIQUE KEY unique_post_category (post_id, category_id),
    
    -- Indexes
    INDEX idx_post_id (post_id),
    INDEX idx_category_id (category_id)
);

-- Create Comments Table (for future blog comments)
CREATE TABLE comments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    post_id INT NOT NULL,
    user_id INT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_approved BOOLEAN DEFAULT FALSE,
    parent_id INT NULL, -- For nested comments
    
    -- Foreign Keys
    CONSTRAINT fk_comments_post_id 
        FOREIGN KEY (post_id) REFERENCES posts(id) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_comments_user_id 
        FOREIGN KEY (user_id) REFERENCES users(id) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_comments_parent_id 
        FOREIGN KEY (parent_id) REFERENCES comments(id) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    
    -- Indexes
    INDEX idx_post_id (post_id),
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at),
    INDEX idx_approved (is_approved),
    INDEX idx_parent_id (parent_id)
);

-- Create User Sessions Table (for session management)
CREATE TABLE user_sessions (
    id VARCHAR(255) PRIMARY KEY,
    user_id INT NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Foreign Key
    CONSTRAINT fk_user_sessions_user_id 
        FOREIGN KEY (user_id) REFERENCES users(id) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    
    -- Indexes
    INDEX idx_user_id (user_id),
    INDEX idx_expires_at (expires_at),
    INDEX idx_active (is_active),
    INDEX idx_created_at (created_at)
);

-- Create Application Settings Table
CREATE TABLE app_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    key_name VARCHAR(100) NOT NULL UNIQUE,
    value TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_key_name (key_name)
);

-- Insert Default Data
-- Insert Default Admin User (password: admin123)
-- Password hash for 'admin123' using bcrypt
INSERT INTO users (username, email, password_hash, first_name, last_name, is_admin) 
VALUES ('admin', 'admin@dockflask.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewfhJUPZE7JOV8jO', 'Admin', 'User', TRUE);

-- Insert Default Categories
INSERT INTO categories (name, description, slug) VALUES 
('Technology', 'Posts about technology and programming', 'technology'),
('Web Development', 'Posts about web development', 'web-development'),
('Flask', 'Posts about Flask framework', 'flask'),
('Python', 'Posts about Python programming', 'python'),
('Docker', 'Posts about Docker and containerization', 'docker');

-- Insert Default Settings
INSERT INTO app_settings (key_name, value, description) VALUES 
('site_name', 'DockFlask Pro', 'The name of the website'),
('site_description', 'Advanced Python Flask Application with MySQL Database', 'Description of the website'),
('posts_per_page', '10', 'Number of posts to display per page'),
('allow_registration', 'true', 'Whether new user registration is allowed'),
('require_email_verification', 'false', 'Whether email verification is required for new users');

-- Insert Sample Blog Post
INSERT INTO posts (title, content, user_id, is_published) VALUES 
('Welcome to DockFlask Pro!', 
'This is your first blog post in DockFlask Pro. You can create, edit, and manage your blog posts through the dashboard. 

Features included:
- User authentication and management
- Blog post creation and management  
- MySQL database integration
- Responsive Bootstrap UI
- RESTful APIs
- Docker containerization

Start exploring and creating amazing content!', 
1, TRUE);

-- Create Views for Analytics
CREATE VIEW user_post_stats AS
SELECT 
    u.id as user_id,
    u.username,
    u.first_name,
    u.last_name,
    COUNT(p.id) as total_posts,
    SUM(CASE WHEN p.is_published = 1 THEN 1 ELSE 0 END) as published_posts,
    SUM(p.views) as total_views,
    MAX(p.created_at) as last_post_date
FROM users u
LEFT JOIN posts p ON u.id = p.user_id
GROUP BY u.id, u.username, u.first_name, u.last_name;

CREATE VIEW popular_posts AS
SELECT 
    p.id,
    p.title,
    p.views,
    p.created_at,
    u.username as author,
    u.first_name,
    u.last_name
FROM posts p
JOIN users u ON p.user_id = u.id
WHERE p.is_published = 1
ORDER BY p.views DESC;

-- Show database structure
SHOW TABLES;
DESCRIBE users;
DESCRIBE posts;
DESCRIBE system_logs;
