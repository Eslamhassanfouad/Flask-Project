from datetime import datetime
from flasktasks import app
from flask_login import  UserMixin
from flasktasks import db , login_manager
from sqlalchemy import event


friends_table = db.Table('friends',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key = True),
    db.Column('friend_id', db.Integer, db.ForeignKey('user.id'),  primary_key = True),
)
requests_table = db.Table('request',
    db.Column('sender_id', db.Integer, db.ForeignKey('user.id' ),  primary_key = True),
    db.Column('reciever_id', db.Integer, db.ForeignKey('user.id'),  primary_key = True)
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    friends = db.relationship('User', 
                              secondary=friends_table,
                              primaryjoin=(friends_table.c.user_id == id),
                              secondaryjoin=(friends_table.c.friend_id == id) ,
                              backref=db.backref('friend_of', lazy='dynamic'),
                              lazy='dynamic')
    requests = db.relationship('User', 
                               secondary=requests_table,
                               primaryjoin=(requests_table.c.sender_id == id),
                               secondaryjoin=(requests_table.c.reciever_id == id),
                               backref=db.backref('requested_to', lazy='dynamic'),
                               lazy='dynamic')
    image = db.Column(db.String(255),nullable=True)
    notifications = db.relationship('Notification', backref='author')

    def __repr__(self):
        return f"(name: {self.name}, email: {self.email})"
    
    
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    privacy = db.Column(db.String(30), nullable=True, default='public')

    def __repr__(self):
        return f"{self.title}, {self.content}, {self.date_posted}"



class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    datetime_posted = db.Column(db.DateTime, default=datetime.now())
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# @event.listens_for(User.friends,'append')
# def on_friend_created(mapper,connection,friendship):
#       print("TRIIIIGGGEREED")
#       with app.app_context():
#         sender_id = friendship.friend_id
#         reciever = User.query.filter(User.id == friendship.user_id).first()
#         notification = Notification(user_id=sender_id,
#                                     description= f"{reciever.name} has accepted your request! You are new freinds."
#                                     )
#         db.session.add(notification)
#         db.session.commit()
# @event.listens_for(User.requests,'append')
# def on_friend_created(mapper,connection,friendship):
#       print("TRIIIIGGGEREED")
      