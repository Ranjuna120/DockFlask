#!/usr/bin/env python3
"""
Setup FAQ system - Create table structure
"""

import sqlite3
import os
from datetime import datetime

def setup_faq_table():
    """Create FAQ table structure"""
    db_path = os.path.join('instance', 'dockflask.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return False
    
    try:
        # Connect to SQLite database
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        
        print(f"Connected to SQLite database: {db_path}")
        
        # Create FAQ table
        create_table_query = """
        CREATE TABLE IF NOT EXISTS faqs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            category VARCHAR(50) DEFAULT 'General',
            display_order INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        cursor.execute(create_table_query)
        print("✅ FAQ table created successfully")
        
        # Check if FAQ table exists and is created
        cursor.execute("SELECT COUNT(*) FROM faqs")
        count = cursor.fetchone()[0]
        print(f"✅ FAQ table created successfully with {count} entries")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if connection:
            connection.rollback()
        return False
        
    finally:
        if connection:
            connection.close()
            print("SQLite connection closed")

if __name__ == "__main__":
    print("🔄 Setting up FAQ system...")
    success = setup_faq_table()
    
    if success:
        print("🎉 FAQ system setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Add FAQ model to models.py")
        print("2. Create FAQ routes in app.py")
        print("3. Create FAQ templates")
        print("4. Add FAQ management to admin dashboard")
    else:
        print("💥 FAQ setup failed!")
