# LinkedIn CRM

A complete CRM system for managing your LinkedIn contacts, with an accompanying browser extension for easy contact import.

## Features

- **User Authentication**: Secure login and registration
- **Contact Management**: Add, edit, view, and delete LinkedIn contacts
- **Tagging System**: Organize contacts with customizable tags
- **Interaction Tracking**: Record emails, calls, meetings, and notes for each contact
- **Chrome Extension**: Directly import contacts from LinkedIn profiles
- **Responsive Design**: Works on desktop and mobile devices

## System Requirements

- Python 3.8+
- MySQL Database
- cPanel hosting with Python support

## Installation and Deployment on cPanel

### 1. Create a MySQL Database in cPanel

1. Log in to your cPanel account
2. Go to "MySQL Databases"
3. Create a new database (e.g., `linkedin_crm`)
4. Create a new user with a strong password
5. Add the user to the database with all privileges

### 2. Upload Application Files

#### Using cPanel File Manager:

1. Compress your application files (excluding virtual environment) into a ZIP archive
2. Upload the ZIP file to your cPanel using File Manager
3. Extract the ZIP in your desired directory (e.g., `linkedin-crm`)

#### Using Git (if supported):

```bash
ssh username@your-cpanel-server
cd public_html
git clone https://github.com/yourusername/linkedin-crm.git
cd linkedin-crm
```

### 3. Set Up Python Environment

Most cPanel hosts use Python Application Manager or Setup Python App:

1. In cPanel, navigate to "Setup Python App"
2. Create a new application:
   - Python version: 3.8+ (select highest available)
   - Application root: `/path/to/linkedin-crm`
   - Application URL: `https://yourdomain.com/linkedin-crm` or use a subdomain
   - Application startup file: `run.py`

### 4. Configure Environment Variables

1. Edit the `.env` file in your application root:

```
FLASK_APP=run.py
FLASK_CONFIG=production
SECRET_KEY=your-secure-random-key-here

# Production database
DATABASE_URL=mysql+pymysql://username:password@localhost/linkedin_crm
```

Replace `username`, `password`, and `linkedin_crm` with your actual MySQL credentials.

### 5. Install Dependencies

In SSH or through cPanel Terminal:

```bash
cd /path/to/linkedin-crm
pip install -r requirements.txt
```

### 6. Initialize the Database

```bash
cd /path/to/linkedin-crm
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 7. Configure Server

#### For cPanel with Passenger:

Create a `.htaccess` file in your application root:

```
RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
PassengerAppRoot /path/to/linkedin-crm
PassengerBaseURI /linkedin-crm
PassengerPython /path/to/python/bin/python3
```

#### For cPanel with WSGI:

Create a `passenger_wsgi.py` file in your application root:

```python
import sys
import os

INTERP = os.path.join(os.environ['HOME'], 'path/to/python/bin/python3')
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

sys.path.append(os.getcwd())
from run import app as application
```

### 8. Restart the Application

In cPanel, go to "Setup Python App" and restart your application.

## Chrome Extension Installation

1. Download the `extension.zip` file from the `extension` directory
2. Unzip the file to a folder on your computer
3. Open Chrome and go to `chrome://extensions/`
4. Enable "Developer mode" using the toggle in the top right
5. Click "Load unpacked" and select the unzipped extension folder
6. The LinkedIn CRM extension will now appear in your Chrome toolbar

## Usage

1. Register a new account at `https://yourdomain.com/linkedin-crm` (or your configured URL)
2. Log in to access your dashboard
3. Install the Chrome extension and configure it with your API key (found in your dashboard)
4. Visit LinkedIn profiles and use the extension to add contacts directly to your CRM
5. Manage your contacts, add tags, and track interactions through the web interface

## Development

### Local Setup

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Set up a local MySQL database
6. Configure your `.env` file with local database credentials
7. Initialize the database: 
   ```
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```
8. Run the application: `flask run`

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues or questions, please contact [your-email@example.com] # linkedin-crm
