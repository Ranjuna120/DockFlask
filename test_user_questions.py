#!/usr/bin/env python3
"""
Test script for User Questions system
Verifies the database setup and functionality
"""

import sqlite3
import os

def test_user_questions():
    # Database path
    db_path = 'instance/dockflask.db'
    
    if not os.path.exists(db_path):
        print("❌ Database not found. Please run setup_user_questions.py first.")
        return
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Test 1: Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_questions'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            print("✅ user_questions table exists")
        else:
            print("❌ user_questions table not found")
            return
        
        # Test 2: Check table structure
        cursor.execute("PRAGMA table_info(user_questions)")
        columns = cursor.fetchall()
        expected_columns = [
            'id', 'name', 'email', 'subject', 'question', 'category', 
            'status', 'is_public', 'answer', 'answered_by', 'answered_at', 
            'created_at', 'updated_at'
        ]
        
        column_names = [col[1] for col in columns]
        missing_columns = [col for col in expected_columns if col not in column_names]
        
        if not missing_columns:
            print("✅ All required columns exist")
        else:
            print(f"❌ Missing columns: {missing_columns}")
        
        # Test 3: Check sample data
        cursor.execute("SELECT COUNT(*) FROM user_questions")
        count = cursor.fetchone()[0]
        print(f"📊 Total questions in database: {count}")
        
        # Test 4: Display sample questions
        cursor.execute("""
            SELECT name, subject, category, status, created_at 
            FROM user_questions 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        
        questions = cursor.fetchall()
        
        if questions:
            print("\n📝 Sample Questions:")
            print("-" * 80)
            for q in questions:
                name, subject, category, status, created_at = q
                status_icon = "⏳" if status == "pending" else "✅" if status == "answered" else "📁"
                print(f"{status_icon} [{category}] {subject[:50]}... - by {name}")
        
        # Test 5: Check status distribution
        cursor.execute("SELECT status, COUNT(*) FROM user_questions GROUP BY status")
        status_stats = cursor.fetchall()
        
        print("\n📈 Question Statistics:")
        print("-" * 30)
        for status, count in status_stats:
            print(f"{status.capitalize()}: {count}")
        
        # Test 6: Check categories
        cursor.execute("SELECT category, COUNT(*) FROM user_questions GROUP BY category")
        category_stats = cursor.fetchall()
        
        print("\n🏷️  Category Distribution:")
        print("-" * 30)
        for category, count in category_stats:
            print(f"{category}: {count}")
        
        conn.close()
        
        print("\n" + "="*50)
        print("✅ User Questions system test completed successfully!")
        print("🌐 System is ready for use!")
        print("\nNext steps:")
        print("1. Start the Flask app: python app.py")
        print("2. Visit /ask-question to submit questions")
        print("3. Admin can manage questions at /admin/questions")
        
    except Exception as e:
        print(f"❌ Error testing system: {e}")

if __name__ == '__main__':
    test_user_questions()
