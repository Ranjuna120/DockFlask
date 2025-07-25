#!/usr/bin/env python3

from app import create_app
from models import db
from sqlalchemy import text

# Create the Flask app
app, login_manager = create_app()

with app.app_context():
    try:
        # Add the category_id column to posts table
        print("Adding category_id column to posts table...")
        db.session.execute(text("ALTER TABLE posts ADD COLUMN category_id INT NULL"))
        db.session.commit()
        print("✅ Column added!")
        
        # Add index for better performance
        print("Adding index for category_id...")
        db.session.execute(text("ALTER TABLE posts ADD INDEX idx_category_id (category_id)"))
        db.session.commit()
        print("✅ Index added!")
        
        # Add foreign key constraint
        print("Adding foreign key constraint...")
        db.session.execute(text("ALTER TABLE posts ADD FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL"))
        db.session.commit()
        print("✅ Foreign key constraint added!")
        
        print("🎉 Database schema updated successfully!")
        
    except Exception as e:
        if "Duplicate column name" in str(e):
            print("✅ Column already exists, skipping...")
        else:
            print(f"❌ Error: {e}")
            db.session.rollback()
