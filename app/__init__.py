from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from app.config.config import config
from app.models.models import db, User
from flask_cors import CORS
import datetime
import jinja2

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
migrate = Migrate()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app(config_name='default'):
    app = Flask(__name__)
    # Add this line after creating the app
    CORS(app)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # Enable CORS for API routes
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Register Jinja2 filters
    app.jinja_env.filters['nl2br'] = nl2br
    
    # Register blueprints
    from app.controllers.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    
    from app.controllers.main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from app.controllers.contacts import contacts as contacts_blueprint
    app.register_blueprint(contacts_blueprint)
    
    from app.controllers.api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')
    
    # Add datetime to all templates
    @app.context_processor
    def inject_now():
        return {'now': datetime.datetime.utcnow()}
    
    return app

# Define nl2br filter for Jinja2
def nl2br(value):
    if value:
        return jinja2.utils.markupsafe.Markup(value.replace('\n', '<br>\n'))
    return "" 