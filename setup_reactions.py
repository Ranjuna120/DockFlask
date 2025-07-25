from app import app
from models import db, PostReaction

def setup_reactions_table():
    with app.app_context():
        print("🔄 Setting up post reactions table...")
        
        try:
            # Create the post_reactions table
            db.create_all()
            print("✅ Post reactions table created successfully!")
            
            # Check if table exists and show structure
            inspector = db.inspect(db.engine)
            if 'post_reactions' in inspector.get_table_names():
                columns = inspector.get_columns('post_reactions')
                print(f"📊 Table structure:")
                for column in columns:
                    print(f"   - {column['name']}: {column['type']}")
            else:
                print("❌ Failed to create post_reactions table!")
                
        except Exception as e:
            print(f"❌ Error setting up reactions table: {e}")

if __name__ == '__main__':
    setup_reactions_table()
