import os
from flask import Flask, send_from_directory

from config import Config
from models import db
import routes

def create_app(config_class=Config):
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints
    from routes import webnote_blueprint
    app.register_blueprint(webnote_blueprint)
    
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
    
    # Route for serving static files
    @app.route('/webnote/<path:filename>')
    def serve_static(filename):
        return send_from_directory('static', filename)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)