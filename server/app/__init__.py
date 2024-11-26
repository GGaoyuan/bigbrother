from flask import Flask

def create_app():
    app = Flask(__name__)
    # app.config.from_object('config.Config')

    from .routes import main_route, test_route
    app.register_blueprint(main_route.bp)
    app.register_blueprint(test_route.bp)
    
    return app