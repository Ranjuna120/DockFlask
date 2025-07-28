#!/usr/bin/env python3
"""
Test the complete user question system with MySQL
"""

from app import app, db
from user_question_model import UserQuestion

def test_question_system():
    with app.app_context():
        print("=== Testing User Question System with MySQL ===")
        
        # Test 1: Create a test question
        print("\n1. Creating a test question...")
        test_question = UserQuestion(
            name="Test User",
            email="test@example.com",
            subject="Test Question Subject",
            question="This is a test question about the system",
            category="Technical",
            status="pending"
        )
        
        db.session.add(test_question)
        db.session.commit()
        
        question_id = test_question.id
        print(f"✅ Question created with ID: {question_id}")
        
        # Test 2: Retrieve all questions
        print("\n2. Retrieving all questions...")
        all_questions = UserQuestion.query.all()
        print(f"✅ Total questions in database: {len(all_questions)}")
        
        for q in all_questions:
            print(f"  - ID: {q.id}, Subject: {q.subject}, Status: {q.status}, Email: {q.email}")
        
        # Test 3: Test filtering by status
        print("\n3. Testing status filtering...")
        pending_questions = UserQuestion.query.filter_by(status='pending').all()
        print(f"✅ Pending questions: {len(pending_questions)}")
        
        # Test 4: Update question (simulate answering)
        print("\n4. Testing question update...")
        test_question.answer = "This is a test answer"
        test_question.status = "answered"
        db.session.commit()
        print("✅ Question answered successfully")
        
        # Test 5: Get statistics
        print("\n5. Getting statistics...")
        from sqlalchemy import func
        stats = db.session.query(UserQuestion.status, func.count(UserQuestion.id)).group_by(UserQuestion.status).all()
        stats_dict = dict(stats)
        print(f"✅ Statistics: {stats_dict}")
        
        print("\n=== Test Complete ===")
        print("✅ All MySQL operations working correctly!")
        print("\nYou can now:")
        print("1. Submit questions via /ask-question")
        print("2. View questions in admin panel at /admin/questions")
        print("3. Answer, delete, or manage questions from admin interface")

if __name__ == "__main__":
    test_question_system()
