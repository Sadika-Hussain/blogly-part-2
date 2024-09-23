"""Models for Blogly."""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)

class User(db.Model):
    """Represents a user in the Blogly application.
    
    Attributes:
        id (int): The primary key for the user.
        first_name (str): The user's first name.
        last_name (str): The user's last name.
        image_url (str): The URL of the user's profile image.
    """
    __tablename__ = "users"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    
    first_name = db.Column(db.String(50),
                     nullable=False)
    
    last_name = db.Column(db.String(50),
                     nullable=False)
    
    image_url = db.Column(db.String)

    posts = db.relationship('Post', backref='user', cascade="all, delete-orphan")

    


    def get_full_name(self):
        """Returns the full name of the user."""
        return f'{self.first_name} {self.last_name}'
    
    def first(self):
        """Returns the first name of the user"""
        return f'{self.first_name}'
    
    def last(self):
        """Returns the last name of the user"""
        return f'{self.last_name}'

    def image(self):
        """Returns the image URL of the user"""
        return f'{self.image_url}'

    @classmethod
    def get_user_by_id(cls, id):
        """Fetches a user by their ID."""
        return cls.query.filter_by(id=id).first()
    


class Post(db.Model):

        __tablename__ = "posts"

        id = db.Column(db.Integer,
                    primary_key=True,
                    autoincrement=True)
        
        title = db.Column(db.Text,
                        nullable=False)
        
        content = db.Column(db.Text,
                        nullable=False)
        
        created_at = db.Column(db.DateTime, default=datetime.now)
        
        user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

        def format_date_time(self):
            formatted_date = self.created_at.strftime("%b %d %Y, %I:%M %p")
            return formatted_date


        @classmethod
        def get_post_by_user_id(cls, id):
            return cls.query.filter_by(user_id=id).all()
        
        @classmethod
        def get_post_by_post_id(cls, id):
            return cls.query.filter_by(id=id).one()
    
        
     

    

    
