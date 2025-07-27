#!/usr/bin/env python3
"""
Setup script for User Questions system
Creates the user_questions table and sets up the system
"""

import sqlite3
import os
from datetime import datetime

def setup_user_questions():
    # Database path
    db_path = 'instance/dockflask.db'
    
    # Create instance directory if it doesn't exist
    os.makedirs('instance', exist_ok=True)
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create user_questions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(120) NOT NULL,
            subject VARCHAR(200) NOT NULL,
            question TEXT NOT NULL,
            category VARCHAR(50) DEFAULT 'General',
            status VARCHAR(20) DEFAULT 'pending',
            is_public BOOLEAN DEFAULT 0,
            answer TEXT,
            answered_by INTEGER,
            answered_at DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (answered_by) REFERENCES users (id)
        )
    ''')
    
    # Create index for faster queries
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_questions_status ON user_questions(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_questions_category ON user_questions(category)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_questions_created ON user_questions(created_at)')
    
    # Commit and close
    conn.commit()
    conn.close()
    
    print("✅ User Questions system setup completed!")
    print(f"📊 Database: {db_path}")
    print("🔧 Created table: user_questions")
    print("📝 Table is ready for real user questions")
    print("\nNext steps:")
    print("1. Run the Flask app")
    print("2. Visit /ask-question to submit questions")
    print("3. Admin can manage questions from dashboard")

if __name__ == '__main__':
    setup_user_questions()
