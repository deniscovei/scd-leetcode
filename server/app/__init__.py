from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .utils.db import init_db
import config
from datetime import timedelta

def create_app():
    app = Flask(__name__)
    CORS(app) # Enable CORS for all routes
    
    # Load configuration
    app.config['SECRET_KEY'] = config.SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URI
    app.config['JWT_SECRET_KEY'] = config.SECRET_KEY # Use same secret for simplicity
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)

    # Initialize the database
    init_db(app)
    
    # Initialize JWT
    jwt = JWTManager(app)

    # Register blueprints
    from .routes.auth import auth_bp
    from .routes.problems import problems_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(problems_bp, url_prefix='/api/problems')

    return app

