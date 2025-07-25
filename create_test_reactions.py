from app import app
from models import db, User, Post, PostReaction
from datetime import datetime

def create_test_reactions():
    with app.app_context():
        print("🔄 Creating test post reactions...")
        
        # Get admin user and posts
        admin_user = User.query.filter_by(username='admin').first()
        posts = Post.query.all()
        
        if not admin_user:
            print("❌ Admin user not found!")
            return
            
        if not posts:
            print("❌ No posts found! Please create some posts first.")
            return
        
        # Create test reactions
        test_reactions = [
            {'post': posts[0], 'user': admin_user, 'type': 'like'},
            {'post': posts[1] if len(posts) > 1 else posts[0], 'user': admin_user, 'type': 'like'},
            {'post': posts[2] if len(posts) > 2 else posts[0], 'user': admin_user, 'type': 'dislike'},
        ]
        
        for reaction_data in test_reactions:
            # Check if reaction already exists
            existing = PostReaction.query.filter_by(
                user_id=reaction_data['user'].id,
                post_id=reaction_data['post'].id
            ).first()
            
            if not existing:
                reaction = PostReaction(
                    user_id=reaction_data['user'].id,
                    post_id=reaction_data['post'].id,
                    reaction_type=reaction_data['type']
                )
                db.session.add(reaction)
        
        db.session.commit()
        
        # Count total reactions
        total_reactions = PostReaction.query.count()
        likes_count = PostReaction.query.filter_by(reaction_type='like').count()
        dislikes_count = PostReaction.query.filter_by(reaction_type='dislike').count()
        
        print(f"✅ Test reactions created successfully!")
        print(f"📊 Total reactions: {total_reactions}")
        print(f"👍 Likes: {likes_count}")
        print(f"👎 Dislikes: {dislikes_count}")

if __name__ == '__main__':
    create_test_reactions()
