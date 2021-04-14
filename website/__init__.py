from flask import Flask, url_for, render_template

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'pokemon pokemon'

    from .views import views
    from .auth import auth
    
    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")
    return app