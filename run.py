import os
from app import create_app
from app.models.models import db
from flask_migrate import upgrade
from dotenv import load_dotenv

load_dotenv()

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

@app.shell_context_processor
def make_shell_context():
    return dict(app=app, db=db)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001) 