from flask import Flask
from flask_login import LoginManager

app = Flask(__name__)
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate



app.config['SECRET_KEY'] = 'WNkYdsV2xKNZBXZQEsAAlweq781SWrOl23Pm'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['UPLOAD_FOLDER'] = 'flasktasks/static/uploads'

db = SQLAlchemy(app)
migrate = Migrate(app, db)
app.cli.add_command('db', Migrate)

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login_endpoint'

from flasktasks import routes
from flasktasks.models import User

