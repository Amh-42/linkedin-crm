from flask import Blueprint, render_template, redirect, request, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.models.models import User, db
from app.controllers.forms import LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm
from app.utils.email import send_verification_email, send_reset_password_email
from datetime import datetime
import os

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.check_password(form.password.data):
            # Check if email is verified
            if not user.is_verified:
                flash('Please verify your email address before logging in. Check your inbox for the verification email.')
                return redirect(url_for('auth.login'))
                
            login_user(user, form.remember_me.data)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('main.index')
            return redirect(next)
        flash('Invalid email or password.')
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, username=form.username.data)
        user.set_password(form.password.data)
        user.verification_sent_at = datetime.utcnow()
        
        db.session.add(user)
        db.session.commit()
        
        # Generate verification token and URL
        token = user.generate_verification_token()
        verification_url = url_for('auth.verify_email', token=token, _external=True)
        
        # Send verification email
        send_verification_email(user, verification_url)
        
        flash('A verification email has been sent to your email address. Please check your inbox to complete registration.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

@auth.route('/verify-email/<token>')
def verify_email(token):
    try:
        email = User.verify_token(token, expiration=86400)  # 24 hours expiration
        if not email:
            flash('The verification link is invalid or has expired.')
            return redirect(url_for('auth.login'))
        
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('User not found.')
            return redirect(url_for('auth.login'))
        
        if user.is_verified:
            flash('Your account is already verified. Please login.')
            return redirect(url_for('auth.login'))
        
        user.is_verified = True
        db.session.commit()
        
        flash('Your email has been verified! You can now login.')
        return redirect(url_for('auth.login'))
        
    except Exception as e:
        flash('An error occurred. Please try again.')
        return redirect(url_for('auth.login'))

@auth.route('/resend-verification')
def resend_verification():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    # Show form to enter email
    return render_template('auth/resend_verification.html')

@auth.route('/resend-verification', methods=['POST'])
def resend_verification_submit():
    email = request.form.get('email')
    if not email:
        flash('Please enter your email address.')
        return redirect(url_for('auth.resend_verification'))
    
    user = User.query.filter_by(email=email).first()
    if not user:
        # Don't reveal that the user doesn't exist
        flash('If your email is registered, a new verification email has been sent.')
        return redirect(url_for('auth.login'))
    
    if user.is_verified:
        flash('Your account is already verified. Please login.')
        return redirect(url_for('auth.login'))
    
    # Generate verification token and URL
    token = user.generate_verification_token()
    verification_url = url_for('auth.verify_email', token=token, _external=True)
    
    # Update verification sent timestamp
    user.verification_sent_at = datetime.utcnow()
    db.session.commit()
    
    # Send verification email
    send_verification_email(user, verification_url)
    
    flash('A new verification email has been sent. Please check your inbox.')
    return redirect(url_for('auth.login'))

@auth.route('/reset-password-request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_verification_token()
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            send_reset_password_email(user, reset_url)
        
        # Don't reveal if a user exists or not
        flash('If your email is registered, we have sent you instructions to reset your password.')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password_request.html', form=form)

@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    # Verify token
    email = User.verify_token(token, expiration=3600)  # 1 hour expiration
    if not email:
        flash('The password reset link is invalid or has expired.')
        return redirect(url_for('auth.login'))
    
    user = User.query.filter_by(email=email).first()
    if not user:
        flash('User not found.')
        return redirect(url_for('auth.login'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        # Ensure account is verified when resetting password
        user.is_verified = True
        db.session.commit()
        
        flash('Your password has been reset.')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', form=form) 