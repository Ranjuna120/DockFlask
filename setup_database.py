#!/usr/bin/env python3
"""
DockFlask Database Setup Script
Automatically creates the MySQL database and tables
"""

import pymysql
import sys
from datetime import datetime

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Mysql@123',
    'charset': 'utf8mb4'
}

def create_database():
    """Create the dockflask_db database"""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        print("🔗 Connected to MySQL server...")
        
        # Create database
        cursor.execute("CREATE DATABASE IF NOT EXISTS dockflask_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print("✅ Database 'dockflask_db' created successfully!")
        
        cursor.close()
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False

def execute_sql_file():
    """Execute the database_setup.sql file"""
    try:
        # Connect to the specific database
        config = DB_CONFIG.copy()
        config['database'] = 'dockflask_db'
        
        connection = pymysql.connect(**config)
        cursor = connection.cursor()
        
        print("📄 Reading database_setup.sql file...")
        
        # Read SQL file
        with open('database_setup.sql', 'r', encoding='utf-8') as file:
            sql_content = file.read()
        
        # Split by semicolons and execute each statement
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        for i, statement in enumerate(statements, 1):
            if statement.upper().startswith(('CREATE', 'INSERT', 'ALTER', 'DROP')):
                try:
                    cursor.execute(statement)
                    print(f"✅ Statement {i} executed successfully")
                except Exception as e:
                    if "already exists" not in str(e).lower():
                        print(f"⚠️  Statement {i} warning: {e}")
        
        connection.commit()
        print("🎉 All database tables and data created successfully!")
        
        # Verify tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"\n📊 Created {len(tables)} tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        cursor.close()
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Error executing SQL file: {e}")
        return False

def verify_setup():
    """Verify the database setup"""
    try:
        config = DB_CONFIG.copy()
        config['database'] = 'dockflask_db'
        
        connection = pymysql.connect(**config)
        cursor = connection.cursor()
        
        # Check admin user
        cursor.execute("SELECT username, email, is_admin FROM users WHERE username = 'admin'")
        admin_user = cursor.fetchone()
        
        if admin_user:
            print(f"👤 Admin user: {admin_user[0]} ({admin_user[1]}) - Admin: {bool(admin_user[2])}")
        
        # Check categories
        cursor.execute("SELECT COUNT(*) FROM categories")
        cat_count = cursor.fetchone()[0]
        print(f"🏷️  Categories: {cat_count}")
        
        # Check settings
        cursor.execute("SELECT COUNT(*) FROM app_settings")
        settings_count = cursor.fetchone()[0]
        print(f"⚙️  App settings: {settings_count}")
        
        cursor.close()
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Error verifying setup: {e}")
        return False

def main():
    print("🚀 DockFlask Database Setup Started")
    print("=" * 50)
    
    # Step 1: Create database
    if not create_database():
        sys.exit(1)
    
    # Step 2: Execute SQL file
    if not execute_sql_file():
        sys.exit(1)
    
    # Step 3: Verify setup
    if not verify_setup():
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 Database setup completed successfully!")
    print("\nLogin credentials:")
    print("  Username: admin")
    print("  Password: admin123")
    print("\nYou can now start your Flask application!")

if __name__ == "__main__":
    main()
