import unittest
from flask import Flask
from models import db, User, Post
from app import app  

app.config['TESTING'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///test_blogly'  # Use a test database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

db.drop_all()
db.create_all()

class BloglyTestCase(unittest.TestCase):
    def setUp(self):
        """Add a sample user and post"""
        User.query.delete()
        Post.query.delete()

        # Add a sample user
        user = User(first_name="Test", last_name="User", image_url = 'https://example.com/image.jpg')
        db.session.add(user)
        db.session.commit()

        # Add a sample post for this user
        post = Post(title="Sample Post", content="Sample content", user_id=user.id)
        db.session.add(post)
        db.session.commit()

        # Store user and post IDs for use in tests
        self.user_id = user.id
        self.post_id = post.id

    def teardown(self):
        db.session.rollback()

    def test_home_redirect(self):
        """Test the home route redirects to /users."""
        with app.test_client() as client:
            response = client.get('/')
            self.assertEqual(response.status_code, 302)  # Check for redirect
            self.assertEqual(response.location, 'http://localhost/users')  # Check redirect location

    def test_list_users(self):
        """Test the list of users page."""
        with app.test_client() as client:
            response = client.get('/users')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Test User', response.data)  # Check if the sample user is displayed


    def test_add_user(self):
        """Test adding a new user."""
        with app.test_client() as client:
            response = client.post('/users/new', data={
                'firstname': 'New',
                'lastname': 'User',
                'url': 'http://example.com/newuser.jpg'
            })
            self.assertEqual(response.status_code, 302)  # Check for redirect
            self.assertEqual(User.query.count(), 2)  # Check user count

    def test_user_detail(self):
        """Test user detail page."""
        with app.test_client() as client:
            response = client.get(f'/users/{self.user_id}')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Test User', response.data)  # Check if user details are displayed

    def test_edit_user(self):
        """Test editing a user."""
        with app.test_client() as client:
            response = client.post(f'/users/{self.user_id}/edit', data={
                'firstname': 'Updated',
                'lastname': 'User',
                'url': 'http://example.com/updateduser.jpg'
            })
            self.assertEqual(response.status_code, 302)  # Check for redirect
            updated_user = User.query.get(self.user_id)
            self.assertEqual(updated_user.first_name, 'Updated')  # Check if user details were updated

    def test_delete_user(self):
        """Test deleting a user."""
        with app.test_client() as client:
            response = client.post(f'/users/{self.user_id}/delete')
            self.assertEqual(response.status_code, 302)  # Check for redirect
            self.assertIsNone(User.query.get(self.user_id))  # Check if user is deleted


    # Tests for part 2
    ################################################
    def test_post_form(self):
        """
        Test the GET request to display the form for creating a new post.
        """
        with app.test_client() as client:
            response = client.get(f'/users/{self.user_id}/posts/new')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Add post for', response.data)

    def test_add_post(self):
        """
        Test the POST request to create a new post.
        """
        with app.test_client() as client:
            data = {'title': 'Test Post', 'content': 'This is a test post.'}
            response = client.post(f'/users/{self.user_id}/posts/new', data=data, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
        
            # Check if the post is created in the database
            post = Post.query.filter_by(title='Test Post').first()
            self.assertIsNotNone(post)
            self.assertEqual(post.content, 'This is a test post.')

    def test_show_post(self):
        """Test the GET request to display a specific post."""
        with app.test_client() as client:
            response = client.get(f'/posts/{self.post_id}')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Sample Post', response.data)

    def test_edit_post_form(self):
        """
        Test the GET request to display the form for editing a post.
        """
        with app.test_client() as client:
            response = client.get(f'/posts/{self.post_id}/edit')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Edit Post', response.data)

    def test_save_edited_post(self):
        """
        Test the POST request to save changes to an edited post.
        """
        # Modify post data via the form
        with app.test_client() as client:
            data = {'title': 'Updated Title', 'content': 'Updated content'}
            response = client.post(f"/posts/{self.post_id}/edit", data=data, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Updated Title', response.data)

        # Re-query the database for the updated post
        updated_post = Post.query.get(self.post_id)  
        self.assertEqual(updated_post.title, 'Updated Title')
        self.assertEqual(updated_post.content, 'Updated content')


    def test_delete_post(self):
        """
        Test the POST request to delete a specific post.
        """
        with app.test_client() as client:
            response = client.post(f'/posts/{self.post_id}/delete', follow_redirects=True)
            self.assertEqual(response.status_code, 200)

        # Check if the post is deleted from the database
        deleted_post = Post.query.get(self.post_id)
        self.assertIsNone(deleted_post)