#!/usr/bin/env python3
"""
Create user_questions table in MySQL database
"""

from app import app, db
from user_question_model import UserQuestion

def create_user_questions_table():
    with app.app_context():
        try:
            print("Creating user_questions table in MySQL database...")
            
            # Create the table
            db.create_all()
            
            print("✅ user_questions table created successfully!")
            
            # Test the table by checking if it exists
            from sqlalchemy import text
            result = db.session.execute(text("SHOW TABLES LIKE 'user_questions'"))
            if result.fetchone():
                print("✅ Table verified in database")
            else:
                print("❌ Table not found in database")
                
        except Exception as e:
            print(f"❌ Error creating table: {e}")

if __name__ == "__main__":
    create_user_questions_table()
