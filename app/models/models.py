from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from flask import current_app

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    contacts = db.relationship('Contact', backref='owner', lazy='dynamic')
    
    # Email verification fields
    is_verified = db.Column(db.Boolean, default=False)
    verification_sent_at = db.Column(db.DateTime, nullable=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_verification_token(self):
        """Generate email verification token"""
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return serializer.dumps(self.email, salt='email-verification')
    
    @staticmethod
    def verify_token(token, expiration=3600):
        """Verify the email token"""
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            email = serializer.loads(
                token,
                salt='email-verification',
                max_age=expiration
            )
            return email
        except SignatureExpired:
            return None
    
    def __repr__(self):
        return f'<User {self.username}>'

class Contact(db.Model):
    __tablename__ = 'contacts'
    
    id = db.Column(db.Integer, primary_key=True)
    linkedin_id = db.Column(db.String(100), index=True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    company = db.Column(db.String(100))
    position = db.Column(db.String(100))
    linkedin_url = db.Column(db.String(255))
    profile_image_url = db.Column(db.String(255))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    interactions = db.relationship('Interaction', backref='contact', lazy='dynamic')
    tags = db.relationship('ContactTag', back_populates='contact', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Contact {self.first_name} {self.last_name}>'

class Tag(db.Model):
    __tablename__ = 'tags'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    contacts = db.relationship('ContactTag', back_populates='tag', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Tag {self.name}>'

class ContactTag(db.Model):
    __tablename__ = 'contact_tags'
    
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), primary_key=True)
    contact = db.relationship('Contact', back_populates='tags')
    tag = db.relationship('Tag', back_populates='contacts')

class Interaction(db.Model):
    __tablename__ = 'interactions'
    
    id = db.Column(db.Integer, primary_key=True)
    interaction_type = db.Column(db.String(64))  # email, call, meeting, note
    notes = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def __repr__(self):
        return f'<Interaction {self.interaction_type} with {self.contact_id}>' 