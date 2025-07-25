#!/usr/bin/env python3

from app import create_app
from models import db, Comment
from sqlalchemy import text

# Create the Flask app
app, login_manager = create_app()

with app.app_context():
    try:
        # Create comments table
        print("Creating comments table...")
        db.create_all()
        print("✅ Comments table created successfully!")
        
        print("🎉 Comment system is now ready!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.session.rollback()
