import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app, render_template

def send_email(to, subject, template, **kwargs):
    """
    Send an email using cPanel email server
    
    :param to: Recipient email address
    :param subject: Email subject
    :param template: The template to use for email body
    :param kwargs: Additional template parameters
    """
    # Get email settings from config
    email_settings = current_app.config.get('EMAIL_SETTINGS', {})
    sender_email = email_settings.get('MAIL_USERNAME', 'noreply@yourdomain.com')
    sender_name = email_settings.get('MAIL_SENDER_NAME', 'LinkedIn CRM')
    
    # Create message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = f'{sender_name} <{sender_email}>'
    msg['To'] = to
    
    # Render HTML email body using template
    html = render_template(f'email/{template}.html', **kwargs)
    
    # Create HTML and plain text parts
    html_part = MIMEText(html, 'html')
    
    # Generate plain text version by stripping HTML (simplistic approach)
    text = html.replace('<br>', '\n').replace('</p>', '\n')
    text = ''.join(c for c in text if c not in '<>{}=/\'\"')
    text_part = MIMEText(text, 'plain')
    
    # Attach parts to email
    msg.attach(text_part)
    msg.attach(html_part)
    
    try:
        # Connect to SMTP server
        server = smtplib.SMTP(
            email_settings.get('MAIL_SERVER', 'localhost'),
            email_settings.get('MAIL_PORT', 587)
        )
        
        # Check if TLS is enabled
        if email_settings.get('MAIL_USE_TLS', True):
            server.starttls()
        
        # Login to SMTP server if credentials are provided
        if email_settings.get('MAIL_USERNAME') and email_settings.get('MAIL_PASSWORD'):
            server.login(
                email_settings.get('MAIL_USERNAME'),
                email_settings.get('MAIL_PASSWORD')
            )
        
        # Send email
        server.sendmail(sender_email, to, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def send_verification_email(user, verification_url):
    """Send account verification email to the user"""
    return send_email(
        to=user.email,
        subject="Verify Your LinkedIn CRM Account",
        template="verification",
        user=user,
        verification_url=verification_url
    )

def send_reset_password_email(user, reset_url):
    """Send password reset email to the user"""
    return send_email(
        to=user.email,
        subject="Reset Your LinkedIn CRM Password",
        template="reset_password",
        user=user,
        reset_url=reset_url
    ) 