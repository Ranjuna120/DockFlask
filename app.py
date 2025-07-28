from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
import os
import webbrowser
import threading
import time
from datetime import datetime
from config import config
from models import db, User, Post, SystemLog, Category, Comment, PostReaction
from forms import LoginForm, RegistrationForm, PostForm, EditProfileForm, ChangePasswordForm, CommentForm, QuestionSubmissionForm

# Log system actions
def log_action(action, details=None):
    try:
        log = SystemLog(
            action=action,
            user_id=current_user.id if current_user.is_authenticated else None,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            details=details
        )
        db.session.add(log)
        db.session.commit()
    except:
        pass

def create_app(config_name=None):
    app = Flask(__name__)
    
    # Configuration
    config_name = config_name or os.getenv('FLASK_ENV', 'default')
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    
    # Login Manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Please log in to access this page.'
    
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))
    
    return app, login_manager

app, login_manager = create_app()

# Routes
@app.route('/')
def home():
    # Get recent posts
    recent_posts = Post.query.filter_by(is_published=True).order_by(Post.created_at.desc()).limit(5).all()
    total_users = User.query.count()
    total_posts = Post.query.filter_by(is_published=True).count()
    
    # Create general stats for all users
    general_stats = {
        'total_users': total_users,
        'total_posts': total_posts,
        'total_views': sum(post.views for post in recent_posts) if recent_posts else 0
    }
    
    # Create user-specific stats if authenticated
    user_stats = None
    if current_user.is_authenticated:
        user_posts = Post.query.filter_by(user_id=current_user.id).all()
        user_stats = {
            'user_posts': len(user_posts),
            'user_views': sum(post.views for post in user_posts) if user_posts else 0,
            'user_comments': 0,  # Add comment functionality later
            'days_active': (datetime.utcnow() - current_user.created_at).days + 1 if current_user.created_at else 1
        }
    
    return render_template('index.html', 
                         recent_posts=recent_posts,
                         general_stats=general_stats,
                         user_stats=user_stats)

@app.route('/api/health')
def health_check():
    try:
        # Check database connection
        db_status = "connected"
        user_count = User.query.count()
    except Exception as e:
        db_status = f"error: {str(e)}"
        user_count = 0
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'message': 'Flask app is running successfully!',
        'database': db_status,
        'users_count': user_count,
        'authenticated_user': current_user.username if current_user.is_authenticated else None
    })

@app.route('/api/info')
def app_info():
    return jsonify({
        'app_name': 'DockFlask',
        'version': '2.0.0',
        'environment': os.getenv('FLASK_ENV', 'production'),
        'python_version': '3.11',
        'database': 'MySQL' if 'mysql' in app.config['SQLALCHEMY_DATABASE_URI'] else 'SQLite',
        'features': ['User Management', 'Authentication', 'Blog Posts', 'Admin Panel']
    })

# Authentication Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            user.last_login = datetime.utcnow()
            db.session.commit()
            flash(f'Welcome back, {user.first_name}!', 'success')
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        flash('Invalid username or password', 'error')
    
    return render_template('auth/login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful!', 'success')
        return redirect(url_for('login'))
    
    return render_template('auth/register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

# Dashboard Routes
@app.route('/dashboard')
@login_required
def dashboard():
    user_posts = Post.query.filter_by(user_id=current_user.id).order_by(Post.created_at.desc()).all()
    recent_activity = SystemLog.query.filter_by(user_id=current_user.id).order_by(SystemLog.timestamp.desc()).limit(10).all()
    
    # Calculate comment statistics
    user_comments = Comment.query.filter_by(user_id=current_user.id).count()
    total_comments_on_user_posts = Comment.query.join(Post).filter(Post.user_id == current_user.id).count()
    
    stats = {
        'total_posts': len(user_posts),
        'published_posts': len([p for p in user_posts if p.is_published]),
        'total_views': sum(p.views for p in user_posts),
        'total_comments': user_comments,  # Comments by this user
        'comments_received': total_comments_on_user_posts,  # Comments on this user's posts
        'total_users': User.query.count(),  # Add total users count
        'recent_posts': user_posts[:5]
    }
    
    return render_template('dashboard/index.html', stats=stats, recent_activity=recent_activity)

# Blog Routes
@app.route('/posts')
def posts():
    page = request.args.get('page', 1, type=int)
    try:
        posts_query = Post.query.filter_by(is_published=True).order_by(Post.created_at.desc())
        posts_list = posts_query.limit(10).offset((page - 1) * 10).all()
        total_posts = posts_query.count()
        
        # Get categories for the filter dropdown
        categories = Category.query.all()
        
        # Simple pagination object
        class SimplePagination:
            def __init__(self, items, page, per_page, total):
                self.items = items
                self.page = page
                self.per_page = per_page
                self.total = total
                self.pages = (total - 1) // per_page + 1
                self.has_prev = page > 1
                self.has_next = page < self.pages
                self.prev_num = page - 1 if self.has_prev else None
                self.next_num = page + 1 if self.has_next else None
        
        pagination = SimplePagination(posts_list, page, 10, total_posts)
        return render_template('blog/posts.html', posts=posts_list, pagination=pagination, categories=categories)
    except Exception as e:
        print(f"Posts route error: {e}")
        posts_list = Post.query.filter_by(is_published=True).order_by(Post.created_at.desc()).limit(10).all()
        categories = Category.query.all()
        return render_template('blog/posts.html', posts=posts_list, pagination=None, categories=categories)

@app.route('/post/<int:id>', methods=['GET', 'POST'])
def post_detail(id):
    post = Post.query.get_or_404(id)
    if not post.is_published and (not current_user.is_authenticated or current_user.id != post.user_id):
        return redirect(url_for('posts'))
    
    # Increment views
    post.views += 1
    db.session.commit()
    
    # Get comments for this post
    comments = Comment.query.filter_by(post_id=id, is_approved=True).order_by(Comment.created_at.desc()).all()
    
    # Comment form
    comment_form = CommentForm()
    if comment_form.validate_on_submit() and current_user.is_authenticated:
        comment = Comment(
            content=comment_form.content.data,
            user_id=current_user.id,
            post_id=id
        )
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been posted!', 'success')
        return redirect(url_for('post_detail', id=id))
    
    return render_template('blog/post_detail.html', post=post, comments=comments, comment_form=comment_form)

@app.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    # Load categories for the dropdown
    categories = Category.query.all()
    form.category_id.choices = [(0, 'No Category')] + [(c.id, c.name) for c in categories]
    
    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            content=form.content.data,
            category_id=form.category_id.data if form.category_id.data != 0 else None,
            is_published=form.is_published.data,
            user_id=current_user.id
        )
        db.session.add(post)
        db.session.commit()
        flash('Post created successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('blog/create_post.html', form=form)

@app.route('/edit_post/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Post.query.get_or_404(id)
    
    # Check if the current user is the author or admin
    if current_user.id != post.user_id and not current_user.is_admin:
        flash('You do not have permission to edit this post.', 'error')
        return redirect(url_for('post_detail', id=id))
    
    form = PostForm()
    # Load categories for the dropdown
    categories = Category.query.all()
    form.category_id.choices = [(0, 'No Category')] + [(c.id, c.name) for c in categories]
    
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.category_id = form.category_id.data if form.category_id.data != 0 else None
        post.is_published = form.is_published.data
        post.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Post updated successfully!', 'success')
        return redirect(url_for('post_detail', id=id))
    
    # Pre-populate form with existing data
    if request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
        form.category_id.data = post.category_id if post.category_id else 0
        form.is_published.data = post.is_published
    
    return render_template('blog/edit_post.html', form=form, post=post)

@app.route('/delete_post/<int:id>', methods=['POST'])
@login_required
def delete_post(id):
    post = Post.query.get_or_404(id)
    
    # Check if the current user is the author or admin
    if current_user.id != post.user_id and not current_user.is_admin:
        flash('You do not have permission to delete this post.', 'error')
        return redirect(url_for('post_detail', id=id))
    
    # Store post title for flash message
    post_title = post.title
    
    # Delete the post
    db.session.delete(post)
    db.session.commit()
    
    flash(f'Post "{post_title}" has been deleted successfully!', 'success')
    return redirect(url_for('posts'))

@app.route('/delete_comment/<int:comment_id>', methods=['POST'])
@login_required
def delete_comment(comment_id):
    # Get the comment
    comment = Comment.query.get_or_404(comment_id)
    
    # Check if user is the author of the comment or an admin
    if comment.user_id != current_user.id and not current_user.is_admin:
        flash('You can only delete your own comments!', 'error')
        return redirect(url_for('post_detail', id=comment.post_id))
    
    post_id = comment.post_id
    
    # Delete the comment
    db.session.delete(comment)
    db.session.commit()
    
    flash('Comment deleted successfully!', 'success')
    return redirect(url_for('post_detail', id=post_id))

@app.route('/api/comments')
@login_required
def get_comments():
    filter_type = request.args.get('filter', 'all')
    sort_type = request.args.get('sort', 'newest')
    
    # Base query
    query = Comment.query.join(Post).join(User)
    
    # Apply filters
    if filter_type == 'my-posts':
        query = query.filter(Post.author_id == current_user.id)
    elif filter_type == 'my-comments':
        query = query.filter(Comment.user_id == current_user.id)
    elif filter_type == 'pending':
        # For future use if comment approval is implemented
        query = query.filter(Comment.is_approved == False)
    elif filter_type == 'approved':
        # For future use if comment approval is implemented
        query = query.filter(Comment.is_approved == True)
    
    # Apply sorting
    if sort_type == 'newest':
        query = query.order_by(Comment.created_at.desc())
    elif sort_type == 'oldest':
        query = query.order_by(Comment.created_at.asc())
    elif sort_type == 'post':
        query = query.join(Post).order_by(Post.title.asc(), Comment.created_at.desc())
    
    comments = query.all()
    
    # Convert to JSON
    comments_json = []
    for comment in comments:
        comments_json.append({
            'id': comment.id,
            'content': comment.content,
            'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M'),
            'author': {
                'id': comment.author.id,
                'username': comment.author.username,
                'first_name': comment.author.first_name,
                'last_name': comment.author.last_name
            },
            'post': {
                'id': comment.post.id,
                'title': comment.post.title
            },
            'can_delete': comment.user_id == current_user.id or current_user.is_admin
        })
    
    return jsonify(comments_json)

@app.route('/api/post/<int:post_id>/react', methods=['POST'])
@login_required
def toggle_post_reaction(post_id):
    try:
        data = request.get_json()
        reaction_type = data.get('type')  # 'like' or 'dislike'
        
        if reaction_type not in ['like', 'dislike']:
            return jsonify({'error': 'Invalid reaction type'}), 400
        
        post = Post.query.get_or_404(post_id)
        
        # Check if user already reacted to this post
        existing_reaction = PostReaction.query.filter_by(
            user_id=current_user.id,
            post_id=post_id
        ).first()
        
        if existing_reaction:
            if existing_reaction.reaction_type == reaction_type:
                # Remove reaction if same type
                db.session.delete(existing_reaction)
                db.session.commit()
                action = 'removed'
            else:
                # Update reaction type
                existing_reaction.reaction_type = reaction_type
                existing_reaction.updated_at = datetime.utcnow()
                db.session.commit()
                action = 'updated'
        else:
            # Create new reaction
            new_reaction = PostReaction(
                user_id=current_user.id,
                post_id=post_id,
                reaction_type=reaction_type
            )
            db.session.add(new_reaction)
            db.session.commit()
            action = 'added'
        
        # Get updated reaction counts
        likes_count = PostReaction.query.filter_by(post_id=post_id, reaction_type='like').count()
        dislikes_count = PostReaction.query.filter_by(post_id=post_id, reaction_type='dislike').count()
        
        # Get current user's reaction
        user_reaction = PostReaction.query.filter_by(
            user_id=current_user.id,
            post_id=post_id
        ).first()
        
        return jsonify({
            'success': True,
            'action': action,
            'likes_count': likes_count,
            'dislikes_count': dislikes_count,
            'user_reaction': user_reaction.reaction_type if user_reaction else None
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/post/<int:post_id>/reactions')
def get_post_reactions(post_id):
    try:
        post = Post.query.get_or_404(post_id)
        
        likes_count = PostReaction.query.filter_by(post_id=post_id, reaction_type='like').count()
        dislikes_count = PostReaction.query.filter_by(post_id=post_id, reaction_type='dislike').count()
        
        user_reaction = None
        if current_user.is_authenticated:
            reaction = PostReaction.query.filter_by(
                user_id=current_user.id,
                post_id=post_id
            ).first()
            user_reaction = reaction.reaction_type if reaction else None
        
        return jsonify({
            'likes_count': likes_count,
            'dislikes_count': dislikes_count,
            'user_reaction': user_reaction
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    
    if form.validate_on_submit():
        # Check if username is being changed and if it's already taken
        if form.username.data != current_user.username:
            existing_user = User.query.filter_by(username=form.username.data).first()
            if existing_user:
                flash('Username is already taken. Please choose a different one.', 'error')
                return render_template('dashboard/edit_profile.html', form=form)
        
        # Check if email is being changed and if it's already taken
        if form.email.data != current_user.email:
            existing_email = User.query.filter_by(email=form.email.data).first()
            if existing_email:
                flash('Email is already registered. Please use a different email.', 'error')
                return render_template('dashboard/edit_profile.html', form=form)
        
        # Update user information
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        
        db.session.commit()
        log_action('profile_updated', f'Profile updated for user {current_user.username}')
        flash('Your profile has been updated successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    # Pre-populate form with current user data
    if request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
    
    return render_template('dashboard/edit_profile.html', form=form)

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        # Verify current password
        if not current_user.check_password(form.current_password.data):
            flash('Current password is incorrect.', 'error')
            return render_template('dashboard/change_password.html', form=form)
        
        # Update password
        current_user.set_password(form.new_password.data)
        db.session.commit()
        log_action('password_changed', f'Password changed for user {current_user.username}')
        flash('Your password has been changed successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('dashboard/change_password.html', form=form)

@app.route('/stats')
@login_required
def stats():
    # User's personal statistics
    user_posts = Post.query.filter_by(user_id=current_user.id).all()
    published_posts = [post for post in user_posts if post.is_published]
    draft_posts = [post for post in user_posts if not post.is_published]
    
    # Calculate user stats
    user_stats = {
        'total_posts': len(user_posts),
        'published_posts': len(published_posts),
        'draft_posts': len(draft_posts),
        'total_views': sum(post.views for post in user_posts) if user_posts else 0,
        'avg_views_per_post': round(sum(post.views for post in user_posts) / len(user_posts), 1) if user_posts else 0,
        'most_viewed_post': max(user_posts, key=lambda x: x.views) if user_posts else None,
        'recent_posts': sorted(user_posts, key=lambda x: x.created_at, reverse=True)[:5],
        'member_since': current_user.created_at,
        'days_active': (datetime.utcnow() - current_user.created_at).days + 1 if current_user.created_at else 1
    }
    
    # General platform statistics (if admin)
    general_stats = None
    if current_user.is_admin:
        all_users = User.query.all()
        all_posts = Post.query.all()
        published_all_posts = Post.query.filter_by(is_published=True).all()
        
        general_stats = {
            'total_users': len(all_users),
            'total_posts': len(all_posts),
            'published_posts': len(published_all_posts),
            'total_views': sum(post.views for post in all_posts) if all_posts else 0,
            'avg_posts_per_user': round(len(all_posts) / len(all_users), 1) if all_users else 0,
            'most_active_user': max(all_users, key=lambda x: len(x.posts)) if all_users else None,
            'recent_users': sorted(all_users, key=lambda x: x.created_at, reverse=True)[:5]
        }
    
    # Monthly post creation data for charts
    from collections import defaultdict
    import calendar
    
    monthly_posts = defaultdict(int)
    for post in user_posts:
        month_key = post.created_at.strftime('%Y-%m')
        monthly_posts[month_key] += 1
    
    # Convert to chart format
    chart_data = {
        'labels': list(monthly_posts.keys())[-6:],  # Last 6 months
        'data': list(monthly_posts.values())[-6:]
    }
    
    return render_template('dashboard/stats.html', 
                         user_stats=user_stats, 
                         general_stats=general_stats,
                         chart_data=chart_data)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/faq')
def faq():
    # Import here to avoid circular imports
    import sqlite3
    
    try:
        # Connect to database and get FAQs
        conn = sqlite3.connect('instance/dockflask.db')
        cursor = conn.cursor()
        
        # Get all active FAQs ordered by category and display_order
        cursor.execute("""
            SELECT question, answer, category, display_order 
            FROM faqs 
            WHERE is_active = 1 
            ORDER BY category, display_order, id
        """)
        
        faqs_data = cursor.fetchall()
        conn.close()
        
        # Group FAQs by category
        faqs_by_category = {}
        categories = set()
        
        for question, answer, category, display_order in faqs_data:
            if category not in faqs_by_category:
                faqs_by_category[category] = []
            
            faqs_by_category[category].append({
                'question': question,
                'answer': answer,
                'display_order': display_order
            })
            categories.add(category)
        
        total_faqs = len(faqs_data)
        categories = sorted(list(categories))
        
        return render_template('faq.html', 
                             faqs_by_category=faqs_by_category,
                             categories=categories,
                             total_faqs=total_faqs)
        
    except Exception as e:
        print(f"Error loading FAQs: {e}")
        # Fallback empty data
        return render_template('faq.html', 
                             faqs_by_category={},
                             categories=[],
                             total_faqs=0)

@app.route('/ask-question', methods=['GET', 'POST'])
def ask_question():
    form = QuestionSubmissionForm()
    
    if form.validate_on_submit():
        try:
            # Import UserQuestion model
            from user_question_model import UserQuestion
            
            # Create new question using SQLAlchemy
            new_question = UserQuestion(
                name=form.name.data,
                email=form.email.data,
                subject=form.subject.data,
                question=form.question.data,
                category=form.category.data,
                status='pending'
            )
            
            # Save to MySQL database
            db.session.add(new_question)
            db.session.commit()
            
            # Log the action
            log_action('question_submitted', f'Question submitted by {form.name.data}: {form.subject.data}')
            
            flash('Your question has been submitted successfully! We will get back to you soon.', 'success')
            return redirect(url_for('ask_question'))
            
        except Exception as e:
            print(f"Error submitting question: {e}")
            db.session.rollback()
            flash('There was an error submitting your question. Please try again.', 'danger')
    
    return render_template('ask_question.html', form=form)

@app.route('/admin/questions')
@login_required
def admin_questions():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('dashboard'))
    
    try:
        # Import UserQuestion model
        from user_question_model import UserQuestion
        
        # Get filter parameters
        status_filter = request.args.get('status', 'all')
        category_filter = request.args.get('category', 'all')
        
        # Build query using SQLAlchemy
        query = UserQuestion.query
        
        if status_filter != 'all':
            query = query.filter(UserQuestion.status == status_filter)
            
        if category_filter != 'all':
            query = query.filter(UserQuestion.category == category_filter)
            
        # Get questions ordered by created_at descending
        questions = query.order_by(UserQuestion.created_at.desc()).all()
        
        # Get statistics
        from sqlalchemy import func
        stats_query = db.session.query(UserQuestion.status, func.count(UserQuestion.id)).group_by(UserQuestion.status).all()
        stats = dict(stats_query)
        
        # Convert questions to dictionaries
        questions_data = [question.to_dict() for question in questions]
        
        return render_template('admin/questions.html', 
                             questions=questions_data,
                             stats=stats,
                             status_filter=status_filter,
                             category_filter=category_filter)
        
    except Exception as e:
        print(f"Error loading questions: {e}")
        flash('Error loading questions.', 'danger')
        return redirect(url_for('dashboard'))

# API Routes for Question Management
@app.route('/api/questions/<int:question_id>/answer', methods=['POST'])
@login_required
def answer_question(question_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        data = request.get_json()
        answer = data.get('answer', '').strip()
        make_public = data.get('make_public', False)
        
        if not answer:
            return jsonify({'success': False, 'message': 'Answer is required'}), 400
        
        # Import UserQuestion model
        from user_question_model import UserQuestion
        
        # Find the question using SQLAlchemy
        question = UserQuestion.query.get(question_id)
        
        if not question:
            return jsonify({'success': False, 'message': 'Question not found'}), 404
        
        # Update the question with answer
        question.answer = answer
        question.status = 'answered'
        question.is_public = make_public
        question.answered_by = current_user.id
        question.answered_at = datetime.utcnow()
        question.updated_at = datetime.utcnow()
        
        # Save changes to database
        db.session.commit()
        
        # Log the action
        log_action('question_answered', f'Answered question ID: {question_id}')
        
        return jsonify({'success': True, 'message': 'Question answered successfully'})
        
    except Exception as e:
        print(f"Error answering question: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Error answering question'}), 500

@app.route('/api/questions/<int:question_id>/make-public', methods=['POST'])
@login_required
def make_question_public(question_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        import sqlite3
        
        conn = sqlite3.connect('instance/dockflask.db')
        cursor = conn.cursor()
        
        # Get question details
        cursor.execute('''
            SELECT subject, question, answer, category, status 
            FROM user_questions 
            WHERE id = ? AND status = 'answered'
        ''', (question_id,))
        
        question_data = cursor.fetchone()
        
        if not question_data:
            return jsonify({'success': False, 'message': 'Question not found or not answered'}), 404
        
        subject, question_text, answer, category, status = question_data
        
        # Add to FAQ table
        cursor.execute('''
            INSERT INTO faqs (question, answer, category, is_active, created_at, updated_at)
            VALUES (?, ?, ?, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        ''', (subject, answer, category))
        
        # Update user question to mark as public
        cursor.execute('''
            UPDATE user_questions 
            SET is_public = 1, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (question_id,))
        
        conn.commit()
        conn.close()
        
        # Log the action
        log_action('question_made_public', f'Made question ID {question_id} public as FAQ')
        
        return jsonify({'success': True, 'message': 'Question added to public FAQ'})
        
    except Exception as e:
        print(f"Error making question public: {e}")
        return jsonify({'success': False, 'message': 'Error making question public'}), 500

@app.route('/api/questions/<int:question_id>/archive', methods=['POST'])
@login_required
def archive_question(question_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        import sqlite3
        
        conn = sqlite3.connect('instance/dockflask.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE user_questions 
            SET status = 'archived', updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (question_id,))
        
        conn.commit()
        conn.close()
        
        # Log the action
        log_action('question_archived', f'Archived question ID: {question_id}')
        
        return jsonify({'success': True, 'message': 'Question archived successfully'})
        
    except Exception as e:
        print(f"Error archiving question: {e}")
        return jsonify({'success': False, 'message': 'Error archiving question'}), 500

@app.route('/api/questions/<int:question_id>/delete', methods=['DELETE'])
@login_required
def delete_question(question_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        # Import UserQuestion model
        from user_question_model import UserQuestion
        
        # Find the question using SQLAlchemy
        question = UserQuestion.query.get(question_id)
        
        if not question:
            return jsonify({'success': False, 'message': 'Question not found'}), 404
        
        # Store question details for logging before deletion
        subject = question.subject
        name = question.name
        
        # Delete the question using SQLAlchemy
        db.session.delete(question)
        db.session.commit()
        
        # Log the action
        log_action('question_deleted', f'Deleted question "{subject}" by {name}')
        
        return jsonify({'success': True, 'message': 'Question deleted successfully'})
        
    except Exception as e:
        print(f"Error deleting question: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Error deleting question'}), 500

@app.route('/api/questions/<int:question_id>', methods=['GET'])
@login_required
def get_question_details(question_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        import sqlite3
        
        conn = sqlite3.connect('instance/dockflask.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, email, subject, question, category, status, 
                   is_public, answer, answered_by, answered_at, created_at
            FROM user_questions 
            WHERE id = ?
        ''', (question_id,))
        
        question_data = cursor.fetchone()
        conn.close()
        
        if not question_data:
            return jsonify({'success': False, 'message': 'Question not found'}), 404
        
        question = {
            'id': question_data[0],
            'name': question_data[1],
            'email': question_data[2],
            'subject': question_data[3],
            'question': question_data[4],
            'category': question_data[5],
            'status': question_data[6],
            'is_public': bool(question_data[7]),
            'answer': question_data[8],
            'answered_by': question_data[9],
            'answered_at': question_data[10],
            'created_at': question_data[11]
        }
        
        return jsonify({'success': True, 'question': question})
        
    except Exception as e:
        print(f"Error getting question details: {e}")
        return jsonify({'success': False, 'message': 'Error getting question details'}), 500

# API Routes and other routes continue here...

def open_browser():
    """Open the default browser to the Flask app URL after a short delay"""
    time.sleep(1.5)  # Wait for Flask server to start
    webbrowser.open('http://127.0.0.1:5000')

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = True  # Always enable debug mode for development
    
    with app.app_context():
        db.create_all()
        
        # Create admin user if not exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@dockflask.com',
                first_name='Admin',
                last_name='User',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin user created: username=admin, password=admin123")
        else:
            # Verify admin password is working
            if not admin.check_password('admin123'):
                print("🔧 Fixing admin password...")
                admin.set_password('admin123')
                db.session.commit()
                print("✅ Admin password fixed!")
            else:
                print("✅ Admin user verified: username=admin, password=admin123")
        
        # Check if categories exist
        category_count = Category.query.count()
        if category_count == 0:
            print("⚠️ No categories found in database. Categories can be added through admin interface.")
        else:
            print(f"✅ Found {category_count} categories in database")
    
    print("🚀 Starting Flask app with auto-reload enabled...")
    print("🔄 Files will be automatically reloaded when changed")
    print("🌐 Access your app at: http://127.0.0.1:5000")
    print("🌍 Opening browser automatically...")
    
    # Start browser in a separate thread
    if os.getenv('WERKZEUG_RUN_MAIN') != 'true':  # Only open browser on main process
        threading.Thread(target=open_browser, daemon=True).start()
    
    app.run(
        host='0.0.0.0', 
        port=port, 
        debug=True,           # Enable debug mode
        use_reloader=True,    # Enable auto-reload
        use_debugger=True,    # Enable debugger
        threaded=True         # Enable threading
    )
