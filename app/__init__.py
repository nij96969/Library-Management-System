from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
from oauthlib.oauth2 import WebApplicationClient
import requests , os
import redis
from rq import Queue

#added to make insecure google logins as in no configuration required for http traffic setup for oauth in google api
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    from app.auth.routes import auth
    from app.main.routes import main
    from app.admin.routes import admin
    from app.librarian.routes import librarian

    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(admin)
    app.register_blueprint(librarian)
    
    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # OAuth 2 client setup
    client = WebApplicationClient(app.config['GOOGLE_CLIENT_ID'])
    app.extensions['oauth_client'] = client

    # Fetch Google's provider configuration
    google_provider_cfg = requests.get(Config.GOOGLE_DISCOVERY_URL).json()
    app.config['GOOGLE_PROVIDER_CFG'] = google_provider_cfg

    # Set up Redis connection and queue
    # redis_conn = redis.Redis()
    # app.queue = Queue('requests', connection=redis_conn)
    
    return app