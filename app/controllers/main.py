from flask import Blueprint, render_template, send_from_directory, current_app, jsonify
from flask_login import login_required, current_user
import os
import zipfile
import tempfile
from app.models.models import Contact, Interaction

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('main/dashboard.html')
    return render_template('main/index.html')

@main.route('/dashboard')
@login_required
def dashboard():
    contacts_count = Contact.query.filter_by(user_id=current_user.id).count()
    recent_contacts = Contact.query.filter_by(user_id=current_user.id).order_by(Contact.created_at.desc()).limit(5).all()
    recent_interactions = Interaction.query.filter_by(user_id=current_user.id).order_by(Interaction.date.desc()).limit(5).all()
    
    return render_template('main/dashboard.html',
                          contacts_count=contacts_count,
                          recent_contacts=recent_contacts,
                          recent_interactions=recent_interactions)

@main.route('/download-extension')
@login_required
def download_extension():
    """Generate a zip file with the extension files for download"""
    try:
        # Create a temporary zip file containing the extension files
        temp_dir = tempfile.gettempdir()
        extension_zip_path = os.path.join(temp_dir, 'extension.zip')
        
        extension_dir = os.path.join(current_app.root_path, '..', 'extension')
        print(f"Extension directory: {extension_dir}")
        print(f"Files in directory: {os.listdir(extension_dir)}")
        
        with zipfile.ZipFile(extension_zip_path, 'w') as zipf:
            # Create an icons directory inside the zip
            zipf.writestr('icons/.keep', '')
            
            # Add all extension files
            for root, dirs, files in os.walk(extension_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, extension_dir)
                    print(f"Adding file to zip: {arcname}")
                    zipf.write(file_path, arcname)
        
        return send_from_directory(directory=temp_dir, 
                                path='extension.zip', 
                                as_attachment=True)
    except Exception as e:
        print(f"Error creating extension zip: {str(e)}")
        return jsonify({"error": str(e)}), 500 