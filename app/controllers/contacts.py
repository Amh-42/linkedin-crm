from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required, current_user
from app.models.models import Contact, Tag, ContactTag, Interaction, db
from app.controllers.forms import ContactForm, InteractionForm
from datetime import datetime

contacts = Blueprint('contacts', __name__)

@contacts.route('/contacts')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    query = request.args.get('q', '')
    tag_filter = request.args.get('tag', '')
    
    contacts_query = Contact.query.filter_by(user_id=current_user.id)
    
    if query:
        contacts_query = contacts_query.filter(
            (Contact.first_name.contains(query)) | 
            (Contact.last_name.contains(query)) | 
            (Contact.email.contains(query)) | 
            (Contact.company.contains(query))
        )
    
    if tag_filter:
        tag = Tag.query.filter_by(name=tag_filter, user_id=current_user.id).first()
        if tag:
            # Get contact IDs with this tag
            contact_ids = db.session.query(ContactTag.contact_id).filter_by(tag_id=tag.id).all()
            contact_ids = [c[0] for c in contact_ids]
            contacts_query = contacts_query.filter(Contact.id.in_(contact_ids))
    
    pagination = contacts_query.order_by(Contact.last_name).paginate(page=page, per_page=20, error_out=False)
    contacts = pagination.items
    
    # Get all tags for filter dropdown
    tags = Tag.query.filter_by(user_id=current_user.id).all()
    
    return render_template('contacts/index.html', 
                          contacts=contacts, 
                          pagination=pagination,
                          query=query,
                          tag_filter=tag_filter,
                          tags=tags)

@contacts.route('/contacts/create', methods=['GET', 'POST'])
@login_required
def create():
    form = ContactForm()
    if form.validate_on_submit():
        contact = Contact(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            phone=form.phone.data,
            company=form.company.data,
            position=form.position.data,
            linkedin_url=form.linkedin_url.data,
            notes=form.notes.data,
            user_id=current_user.id
        )
        db.session.add(contact)
        db.session.commit()
        
        # Process tags
        if form.tags.data:
            tag_names = [t.strip() for t in form.tags.data.split(',')]
            for tag_name in tag_names:
                if not tag_name:
                    continue
                tag = Tag.query.filter_by(name=tag_name, user_id=current_user.id).first()
                if not tag:
                    tag = Tag(name=tag_name, user_id=current_user.id)
                    db.session.add(tag)
                    db.session.commit()
                contact_tag = ContactTag(contact_id=contact.id, tag_id=tag.id)
                db.session.add(contact_tag)
            db.session.commit()
        
        flash('Contact added successfully.')
        return redirect(url_for('contacts.view', id=contact.id))
    return render_template('contacts/create.html', form=form)

@contacts.route('/contacts/<int:id>')
@login_required
def view(id):
    contact = Contact.query.get_or_404(id)
    # Ensure the contact belongs to the current user
    if contact.user_id != current_user.id:
        abort(403)
    
    interaction_form = InteractionForm()
    
    # Get all interactions for this contact
    interactions = Interaction.query.filter_by(contact_id=contact.id).order_by(Interaction.date.desc()).all()
    
    # Get all tags for this contact
    contact_tags = [ct.tag for ct in contact.tags]
    
    return render_template('contacts/view.html', 
                          contact=contact, 
                          interaction_form=interaction_form, 
                          interactions=interactions,
                          tags=contact_tags)

@contacts.route('/contacts/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    contact = Contact.query.get_or_404(id)
    if contact.user_id != current_user.id:
        abort(403)
        
    form = ContactForm()
    if form.validate_on_submit():
        contact.first_name = form.first_name.data
        contact.last_name = form.last_name.data
        contact.email = form.email.data
        contact.phone = form.phone.data
        contact.company = form.company.data
        contact.position = form.position.data
        contact.linkedin_url = form.linkedin_url.data
        contact.notes = form.notes.data
        contact.updated_at = datetime.utcnow()
        
        # Process tags
        # Remove old tags
        ContactTag.query.filter_by(contact_id=contact.id).delete()
        
        # Add new tags
        if form.tags.data:
            tag_names = [t.strip() for t in form.tags.data.split(',')]
            for tag_name in tag_names:
                if not tag_name:
                    continue
                tag = Tag.query.filter_by(name=tag_name, user_id=current_user.id).first()
                if not tag:
                    tag = Tag(name=tag_name, user_id=current_user.id)
                    db.session.add(tag)
                    db.session.commit()
                contact_tag = ContactTag(contact_id=contact.id, tag_id=tag.id)
                db.session.add(contact_tag)
        
        db.session.commit()
        flash('Contact updated successfully.')
        return redirect(url_for('contacts.view', id=contact.id))
    
    # Populate the form with existing data
    form.first_name.data = contact.first_name
    form.last_name.data = contact.last_name
    form.email.data = contact.email
    form.phone.data = contact.phone
    form.company.data = contact.company
    form.position.data = contact.position
    form.linkedin_url.data = contact.linkedin_url
    form.notes.data = contact.notes
    
    # Get existing tags
    contact_tags = [ct.tag.name for ct in contact.tags]
    form.tags.data = ', '.join(contact_tags)
    
    return render_template('contacts/edit.html', form=form, contact=contact)

@contacts.route('/contacts/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    contact = Contact.query.get_or_404(id)
    if contact.user_id != current_user.id:
        abort(403)
        
    # Delete associated interactions and tags
    Interaction.query.filter_by(contact_id=contact.id).delete()
    ContactTag.query.filter_by(contact_id=contact.id).delete()
    
    db.session.delete(contact)
    db.session.commit()
    flash('Contact deleted.')
    return redirect(url_for('contacts.index'))

@contacts.route('/contacts/<int:id>/interactions', methods=['POST'])
@login_required
def add_interaction(id):
    contact = Contact.query.get_or_404(id)
    if contact.user_id != current_user.id:
        abort(403)
        
    form = InteractionForm()
    if form.validate_on_submit():
        interaction = Interaction(
            interaction_type=form.interaction_type.data,
            notes=form.notes.data,
            contact_id=contact.id,
            user_id=current_user.id
        )
        db.session.add(interaction)
        db.session.commit()
        flash('Interaction added.')
    
    return redirect(url_for('contacts.view', id=contact.id)) 