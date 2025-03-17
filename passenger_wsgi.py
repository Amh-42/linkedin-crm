import os
import sys

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(__file__))

# Import the Flask app
from run import app as application

# Uncomment if using virtualenv with Passenger
# INTERP = os.path.join(os.environ['HOME'], 'path/to/venv/bin/python')
# if sys.executable != INTERP:
#     os.execl(INTERP, INTERP, *sys.argv) 