from flask import Flask
app = Flask(__name__)
from flasktasks import routes

app.config['SECRET_KEY'] = 'WNkYdsV2xKNZBXZQEsAAlweq781SWrOl23Pm'
