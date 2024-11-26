from flask import Flask

def create_app():
    app = Flask(__name__)
    # app.config.from_object('config.Config')

    from .routes import main_route
    app.register_blueprint(main_route.main_bp)
    
    return app