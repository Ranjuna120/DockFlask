#!/usr/bin/env python3

from flask_migrate import init, migrate, upgrade
from app import create_app
import os

# Create the Flask app
app, login_manager = create_app()

with app.app_context():
    # Check if migrations folder exists
    if not os.path.exists('migrations'):
        print("Initializing migrations...")
        init()
        print("✅ Migrations initialized!")
    
    # Create migration for the new category_id column
    print("Creating migration for category support...")
    migrate(message="Add category support to posts")
    print("✅ Migration created!")
    
    # Apply the migration
    print("Applying migration...")
    upgrade()
    print("✅ Migration applied successfully!")
    
print("🎉 Database updated with category support!")
