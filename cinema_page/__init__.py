from flask import Flask
def create_app():
    app = Flask(__name__)
    app.secret_key="my"
    from  .views import create
    app.register_blueprint(create.cr)
    return app