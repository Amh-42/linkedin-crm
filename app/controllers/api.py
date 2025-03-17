from flask import Blueprint, request, jsonify, abort
from flask_login import login_required, current_user
from app.models.models import Contact, Tag, ContactTag, db, User
from datetime import datetime
from functools import wraps
import json

api = Blueprint('api', __name__)

def token_auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid Authorization header'}), 401
            
        token = auth_header.split('Bearer ')[1]
        
        # Parse the token (format: user_id_username)
        parts = token.split('_')
        if len(parts) != 2:
            return jsonify({'error': 'Invalid API key format'}), 401
            
        user_id, username = parts
        
        # Validate user
        user = User.query.filter_by(id=user_id, username=username).first()
        if not user:
            return jsonify({'error': 'Invalid API key'}), 401
            
        # Set the current user for this request
        request.user = user
        
        return f(*args, **kwargs)
    return decorated_function

@api.route('/contacts', methods=['POST'])
@token_auth_required
def create_contact():
    """API endpoint to create a contact from LinkedIn browser extension"""
    data = request.json
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    required_fields = ['first_name', 'last_name']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Get the authenticated user
    user = request.user
    
    # Check if contact already exists by LinkedIn ID or URL
    existing_contact = None
    if 'linkedin_id' in data and data['linkedin_id']:
        existing_contact = Contact.query.filter_by(linkedin_id=data['linkedin_id'], user_id=user.id).first()
    
    if not existing_contact and 'linkedin_url' in data and data['linkedin_url']:
        existing_contact = Contact.query.filter_by(linkedin_url=data['linkedin_url'], user_id=user.id).first()
    
    # Update existing contact or create new one
    if existing_contact:
        for key, value in data.items():
            if key not in ['id', 'user_id', 'created_at']:
                setattr(existing_contact, key, value)
        existing_contact.updated_at = datetime.utcnow()
        contact = existing_contact
        message = 'Contact updated successfully'
    else:
        # Create new contact
        contact_data = {
            'user_id': user.id,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        # Map fields from LinkedIn data to our model
        field_mapping = {
            'first_name': 'first_name',
            'last_name': 'last_name',
            'email': 'email',
            'phone': 'phone',
            'company': 'company',
            'position': 'position',
            'linkedin_url': 'linkedin_url',
            'profile_image_url': 'profile_image_url',
            'linkedin_id': 'linkedin_id',
            'notes': 'notes'
        }
        
        for api_field, model_field in field_mapping.items():
            if api_field in data:
                contact_data[model_field] = data[api_field]
        
        contact = Contact(**contact_data)
        db.session.add(contact)
        db.session.commit()
        message = 'Contact created successfully'
    
    # Process tags if provided
    if 'tags' in data and data['tags']:
        # If existing contact, remove old tags
        if existing_contact:
            ContactTag.query.filter_by(contact_id=contact.id).delete()
        
        # Add tags
        tags = data['tags']
        if isinstance(tags, str):
            # Handle comma-separated string
            tags = [t.strip() for t in tags.split(',')]
        
        for tag_name in tags:
            if not tag_name:
                continue
                
            tag = Tag.query.filter_by(name=tag_name, user_id=user.id).first()
            if not tag:
                tag = Tag(name=tag_name, user_id=user.id)
                db.session.add(tag)
                db.session.commit()
            
            contact_tag = ContactTag(contact_id=contact.id, tag_id=tag.id)
            db.session.add(contact_tag)
    
    db.session.commit()
    
    return jsonify({
        'message': message,
        'contact_id': contact.id
    }), 200 if existing_contact else 201

@api.route('/token_check', methods=['GET'])
@token_auth_required
def token_check():
    """Simple endpoint to check if user's token is valid"""
    user = request.user
    return jsonify({
        'status': 'success',
        'user_id': user.id,
        'username': user.username
    }) 