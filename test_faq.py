#!/usr/bin/env python3
"""
Test FAQ functionality
"""

import sqlite3
import os

def test_faq_data():
    """Test if FAQ data exists and is accessible"""
    db_path = os.path.join('instance', 'dockflask.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Test FAQ table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='faqs'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("❌ FAQ table does not exist")
            return False
        
        print("✅ FAQ table exists")
        
        # Get FAQ data
        cursor.execute("""
            SELECT question, answer, category, display_order 
            FROM faqs 
            WHERE is_active = 1 
            ORDER BY category, display_order, id
        """)
        
        faqs_data = cursor.fetchall()
        
        if not faqs_data:
            print("❌ No FAQ data found")
            return False
        
        print(f"✅ Found {len(faqs_data)} FAQ entries")
        
        # Group by category
        categories = {}
        for question, answer, category, display_order in faqs_data:
            if category not in categories:
                categories[category] = 0
            categories[category] += 1
        
        print("📊 FAQ Categories:")
        for category, count in categories.items():
            print(f"   - {category}: {count} questions")
        
        # Show available questions  
        print("\n📝 Available FAQ Questions:")
        for i, (question, answer, category, display_order) in enumerate(faqs_data[:5]):
            print(f"   {i+1}. [{category}] {question}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error testing FAQ data: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing FAQ functionality...")
    success = test_faq_data()
    
    if success:
        print("\n🎉 FAQ system is ready!")
        print("\n📋 To access the FAQ page:")
        print("1. Start the Flask app: python app.py")
        print("2. Visit: http://127.0.0.1:5000/faq")
        print("3. Check the navigation menu for 'FAQ' link")
    else:
        print("\n💥 FAQ system test failed!")
        print("Run: python setup_faq.py to set up the FAQ system")
