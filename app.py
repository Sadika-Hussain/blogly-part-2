"""Blogly application."""

from flask import Flask, render_template, redirect, request
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Post

app = Flask(__name__)

# Application configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'oh-so-secret'

# Debug Toolbar
debug = DebugToolbarExtension(app)
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

# Database setup
connect_db(app)
db.create_all()

@app.route("/")
def home():
    """Redirect to the list of users."""
    return redirect('users')

@app.route("/users")
def list_users():
    """Display a list of all users."""
    users = User.query.all()
    return render_template("/user/user_list.html", users=users)

@app.route("/users/new")
def add_user():
    """Show form to add a new user."""
    return render_template("/user/user_form.html")


@app.route("/users/new", methods = ['POST'])
def post_user():
    """Handle form submission to add a new user."""
    first_name = request.form.get('firstname')
    last_name = request.form.get('lastname')
    image_url = request.form.get('url')

    # Create a new user and save to the database
    user = User(first_name = first_name, last_name = last_name, image_url = image_url)

    db.session.add(user)
    db.session.commit()

   
    return redirect('/users')

@app.route('/users/<int:user_id>', methods =['POST', 'GET'])
def user_detail(user_id):
    """Show details for a specific user by ID."""
    user = User.get_user_by_id(user_id)

    posts = Post.get_post_by_user_id(user_id)

    return render_template('/user/user_detail.html', user=user, posts = posts)

@app.route('/users/<int:user_id>/edit')
def edit(user_id):
    """Show form to edit an existing user."""
    user = user = User.get_user_by_id(user_id)
    return render_template('/user/user_edit.html', user=user)

@app.route('/users/<int:user_id>/edit', methods = ['POST'])
def save_edits(user_id):
    """Handle form submission to save edits to an existing user."""
    first_name = request.form.get('firstname')
    last_name = request.form.get('lastname')
    image_url = request.form.get('url')

    # Update user details
    user = User.get_user_by_id(user_id)
    user.first_name = first_name
    user.last_name = last_name
    user.image_url = image_url 
    
    # Commit updates to database
    db.session.add(user)
    db.session.commit()

    return redirect(f'/users/{user_id}')

@app.route('/users/<int:user_id>/delete', methods = ['POST'])
def delete_user(user_id):
    """Delete a user by their ID and update database."""
    User.query.filter_by(id = user_id).delete()
    db.session.commit()

    return redirect('/users')


@app.route('/users/<int:user_id>/posts/new')
def post_form(user_id):
    """ Display the form for creating a new post for a given user."""
    user = user = User.get_user_by_id(user_id)
    return render_template('/post/post_form.html', user = user)

@app.route('/users/<int:user_id>/posts/new', methods=['POST'])
def add_post(user_id):
    """Handle the POST request to create a new post for the user"""
    title = request.form.get('title')
    content = request.form.get('content')

    post = Post(title = title, content = content, user_id=user_id)

    db.session.add(post)
    db.session.commit()

    return redirect(f'/users/{user_id}')



@app.route('/posts/<int:post_id>', methods=['GET', 'POST'])
def show_post(post_id):
    """ Display the details of a specific post. """
    post = Post.get_post_by_post_id(post_id)

    return render_template('/post/post_detail.html', post=post)

@app.route('/posts/<int:post_id>/edit')
def edit_post_form(post_id):
        """ Display the form for editing an existing post."""
        post = Post.get_post_by_post_id(post_id)
        return render_template('/post/post_edit.html', post=post)

@app.route('/posts/<int:post_id>/edit', methods=['POST'])
def save_edited_post(post_id):
        """ Handle the POST request to save changes to an edited post. """
        post = Post.get_post_by_post_id(post_id)

        post.title = request.form.get('title')
        post.content = request.form.get('content')

        db.session.add(post)
        db.session.commit()

        return redirect(f'/posts/{post_id}')

@app.route('/posts/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    """Handle the POST request to delete a specific post and update the database"""

    post = Post.get_post_by_post_id(post_id)

    user_id = post.user_id

    Post.query.filter_by(id=post_id).delete()

    db.session.commit()

    return redirect(f'/users/{user_id}')


     

    









