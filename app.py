from datetime import timedelta
from flask import Flask

from flask_cors import CORS
from flask_compress import Compress


app = Flask(__name__, static_folder='static', static_url_path='')
app.config['SECRET_KEY'] = 'restful-backend-session-secret-key'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)

CORS(app, supports_credentials=True)
Compress(app)
