from app import app
from models import db, User, Post, Comment
from datetime import datetime, timedelta

def create_test_comments():
    with app.app_context():
        print("🔄 Creating test comments...")
        
        # Get users and posts
        admin_user = User.query.filter_by(username='admin').first()
        posts = Post.query.all()
        
        if not admin_user:
            print("❌ Admin user not found!")
            return
            
        if not posts:
            print("❌ No posts found! Please create some posts first.")
            return
        
        # Create test comments
        test_comments = [
            {
                'content': 'This is a great post! Thanks for sharing your insights.',
                'post': posts[0],
                'author': admin_user,
                'created_at': datetime.utcnow() - timedelta(days=2)
            },
            {
                'content': 'I found this really helpful. Could you write more about this topic?',
                'post': posts[0] if len(posts) > 0 else posts[0],
                'author': admin_user,
                'created_at': datetime.utcnow() - timedelta(days=1)
            },
            {
                'content': 'Interesting perspective! I have a different view on this matter.',
                'post': posts[1] if len(posts) > 1 else posts[0],
                'author': admin_user,
                'created_at': datetime.utcnow() - timedelta(hours=12)
            },
            {
                'content': 'Thank you for this detailed explanation. Very well written!',
                'post': posts[1] if len(posts) > 1 else posts[0],
                'author': admin_user,
                'created_at': datetime.utcnow() - timedelta(hours=6)
            },
            {
                'content': 'Looking forward to more content like this. Keep up the good work!',
                'post': posts[2] if len(posts) > 2 else posts[0],
                'author': admin_user,
                'created_at': datetime.utcnow() - timedelta(hours=2)
            }
        ]
        
        for comment_data in test_comments:
            # Check if comment already exists to avoid duplicates
            existing = Comment.query.filter_by(
                content=comment_data['content'],
                post_id=comment_data['post'].id,
                user_id=comment_data['author'].id
            ).first()
            
            if not existing:
                comment = Comment(
                    content=comment_data['content'],
                    post_id=comment_data['post'].id,
                    user_id=comment_data['author'].id,
                    created_at=comment_data['created_at']
                )
                db.session.add(comment)
        
        db.session.commit()
        
        # Count total comments
        total_comments = Comment.query.count()
        print(f"✅ Test comments created successfully! Total comments: {total_comments}")

if __name__ == '__main__':
    create_test_comments()
