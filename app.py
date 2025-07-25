from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
import os
import webbrowser
import threading
import time
from datetime import datetime
from config import config
from models import db, User, Post, SystemLog
from forms import LoginForm, RegistrationForm, PostForm, EditProfileForm, ChangePasswordForm

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
    
    stats = {
        'total_posts': len(user_posts),
        'published_posts': len([p for p in user_posts if p.is_published]),
        'total_views': sum(p.views for p in user_posts),
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
        return render_template('blog/posts.html', posts=posts_list, pagination=pagination)
    except Exception as e:
        print(f"Posts route error: {e}")
        posts_list = Post.query.filter_by(is_published=True).order_by(Post.created_at.desc()).limit(10).all()
        return render_template('blog/posts.html', posts=posts_list, pagination=None)

@app.route('/post/<int:id>')
def post_detail(id):
    post = Post.query.get_or_404(id)
    if not post.is_published and (not current_user.is_authenticated or current_user.id != post.user_id):
        return redirect(url_for('posts'))
    
    # Increment views
    post.views += 1
    db.session.commit()
    
    return render_template('blog/post_detail.html', post=post)

@app.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            content=form.content.data,
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
    
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.is_published = form.is_published.data
        post.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Post updated successfully!', 'success')
        return redirect(url_for('post_detail', id=id))
    
    # Pre-populate form with existing data
    if request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
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

@app.route('/about')
def about():
    return render_template('about.html')

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
