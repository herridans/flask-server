from flask import Flask
from db import db
import users

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)

    app.config['MYSQL_HOST'] = "localhost"
    app.config['MYSQL_USER'] = "root"
    app.config['MYSQL_PASSWORD'] = "admin"
    app.config['MYSQL_DB'] = "test"
    app.config['SECRET_KEY'] = ''

    db.init_app(app)

    app.register_blueprint(users.bp)

    return app