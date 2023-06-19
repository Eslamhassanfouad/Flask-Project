from sqlite3 import IntegrityError
from flask import render_template, redirect, url_for, flash,request
import sqlalchemy 
from sqlalchemy import insert , and_ , event 
from flasktasks import app , forms,db, bcrypt , login_manager
from flasktasks.models import User , friends_table , requests_table , Notification,Post
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.utils import secure_filename
import os

nav_items = [
    {'name': 'Home', 'url': '/home'},
    {'name': 'Register', 'url': '/register'},
    {'name': 'Login', 'url': '/login'}


]

@app.route('/home')
def home_endpoint():
    if current_user.is_authenticated:
        nav_items = [
    {'name': 'Home', 'url': '/home'},
    {'name': 'Profile', 'url': f'/profile/{current_user.id}'},
    {'name': 'Logout', 'url': '/logout'}
]
    else:
        nav_items = [
    {'name': 'Home', 'url': '/home'},
    {'name': 'Login', 'url': '/login'}
]  
    
    privacy = request.args.get('privacy')
    with app.app_context():
         if privacy == 'friends':
              user_friends = [friend.id for friend in current_user.friends ]
              posts = db.session.query(Post, User).join(Post,and_(User.id == Post.user_id, Post.user_id.in_(user_friends))).all()
              print(posts)
         else:     
            posts = db.session.query(Post, User).join(Post, and_(User.id == Post.user_id, Post.privacy=='public')).all()
        
    return render_template('home.html' , nav_items=nav_items , posts=posts)

@app.route('/register' , methods=['POST','GET'])
def register_endpoint():
    register_form = forms.RegisterForm()
    if register_form.validate_on_submit():
        image = request.files['image']
        if image:
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image.filename))
            url = image.filename
        else:
            url = 'default.jpg'
        try:
                  with app.app_context():
                            hashed_pw = bcrypt.generate_password_hash(register_form.password1.data).decode('utf-8')
                            new_user = User(
                                name=register_form.name.data,
                                email=register_form.email.data,
                                password=hashed_pw,
                                image = url
                            )
                            db.session.add(new_user)
                            db.session.commit()

                            flash(f"Registration Successful for {register_form.email.data}!")
                            return redirect(url_for('home_endpoint'))
        except sqlalchemy.exc.IntegrityError:
                    flash(f"Email Already Exists!")
                    return redirect(url_for('register_endpoint'))    
    return render_template('register.html', data = {'form': register_form , 'nav_items': nav_items})

@app.route('/login' , methods=['POST','GET'])
def login_endpoint():
    flag = False
    login_form = forms.LoginForm()
    if login_form.validate_on_submit():
        with app.app_context():
            user = User.query.filter_by(email=login_form.email.data).first()
            if user and bcrypt.check_password_hash(user.password, login_form.password.data):
                login_user(user)
                flash(f"Logging in Successful for {login_form.email.data}!")
                return redirect(url_for('home_endpoint'))
            else:   
                    print("Login Failed")
                    flash(f"Invalid email or password")
                    return render_template('login.html', data = {'form': login_form , 'nav_items': nav_items})
                
    return render_template('login.html', data = {'form': login_form , 'nav_items': nav_items})


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login_endpoint'))

@app.route('/profile/<int:id>',methods=['GET','POST'])
@login_required
def profile(id):
    status = "NotFriend"
    nav_items = [
    {'name': 'Home', 'url': '/home'},
    {'name': 'Profile', 'url': f'/profile/{current_user.id}'},
    {'name': 'Logout', 'url': '/logout'}


]
    if request.method=='POST':
        title=request.form['title']
        content=request.form['content']
        user_id=current_user.id
        privacy = request.form['privacy']
        new_post = Post(title=title, content=content, user_id = user_id, privacy = privacy)
        db.session.add(new_post)
        db.session.commit()

    if check_request(id , current_user.id):
         status = "Requested"
    if is_friend(id , current_user.id):
         status = "Friend"
    if status == "NotFriend" or status == "Requested":
         posts = Post.query.filter_by(user_id=id,privacy='public')      
    else:         
         posts = Post.query.filter_by(user_id=id)
    if id == current_user.id:
         posts =  Post.query.filter_by(user_id=id)     
    user = User.query.filter_by(id=id).first()
    if user:
        return render_template('profile.html', posts=posts,nav_items=nav_items, user=user, status=status)
    else:
         return render_template('not_found.html')




@app.route('/delete_post/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted successfully', 'danger')
    return redirect(f'/profile/{current_user.id}')




@app.route('/users')
def show_users():
    
      with app.app_context():
            users = User.query.all()
            for user in users:
                  print(user.name)
            return render_template('users.html', data = {'users': users})
      


@app.route('/request/<int:reciever_id>')
@login_required
def send_request(reciever_id):
      sender_id = current_user.id
      with app.app_context():
            new_request = {
                  'sender_id' : sender_id,
                  'reciever_id' : reciever_id
            }
            stmt = insert(requests_table).values(new_request)
            db.session.execute(stmt)
            db.session.commit()
            send_notification({
                  'user_id' : reciever_id,
                  'friend_id' : sender_id
            },
            'request sent')
      return redirect(request.referrer)



@app.route('/requests')
@login_required
def show_requests():
    with app.app_context():
        # requests = current_user.requests.join(User, current_user.id == requests_table.c.sender_id).all()
        requests = db.session.query(User, requests_table).join(requests_table, and_(User.id == requests_table.c.sender_id, requests_table.c.reciever_id == current_user.id)).all()
        print(f"Requests : {requests}")
        for request in requests:
              print(request[0].image)
              print(request[1])
    return render_template('requests.html', data = {'requests':requests})




@app.route('/requests/delete/<int:reciever_id>/<int:sender_id>')
@login_required
def delete_request(reciever_id, sender_id):
      with app.app_context():
            query = db.session.query(requests_table).filter_by(reciever_id=reciever_id, sender_id=sender_id).delete()  
            db.session.commit()

      return redirect(url_for('show_requests'))    


@app.route('/requests/confirm/<int:reciever_id>/<int:sender_id>')
@login_required
def confirm_request(reciever_id, sender_id):
      with app.app_context():
            new_friend_for_reciever = {
                  'user_id' : reciever_id,
                  'friend_id' : sender_id
            }
            new_friend_for_sender= {
                  'user_id' : sender_id,
                  'friend_id' : reciever_id
            }
            stmt = insert(friends_table).values(new_friend_for_reciever)
            db.session.execute(stmt)
            stmt = insert(friends_table).values(new_friend_for_sender)
            db.session.execute(stmt)
            db.session.commit()
            send_notification(new_friend_for_reciever , 'friend accepted')
            delete_request(reciever_id, sender_id)
      return redirect(url_for('show_requests'))

@app.route('/friends')
@login_required
def show_friends():
      friends = current_user.friends.all()
      print(friends)
      return render_template('friends.html', data = {'friends':friends})


def send_notification(friendship , type):
      with app.app_context():
        sender_id = friendship['friend_id']
        reciever = User.query.filter(User.id == friendship['user_id']).first()
        sender = User.query.filter(User.id == friendship['friend_id']).first()
        if type == 'friend accepted':
            description = f"{reciever.name} has accepted your request! You are now friends."
            id = sender_id
        else:    
            description = f"{sender.name} has sen you a friend request."
            id = reciever.id
        notification = Notification(user_id=id,
                                          description= description
                                          )
        db.session.add(notification)
        db.session.commit()


@app.route('/notifications')
@login_required
def show_notifications():
      notifications = current_user.notifications
      return render_template('notifications.html', data = {'notifications':notifications})


def check_request(sender_id , reciever_id):
     with app.app_context():
          request_sent = db.session.query(requests_table).filter_by(sender_id=sender_id, reciever_id = reciever_id).first()
          request_received = db.session.query(requests_table).filter_by(sender_id=reciever_id, reciever_id = sender_id).first()
          print(request_received)
          print(request_sent)
          return request_sent is not None or request_received is not None


def is_friend(user1_id, user2_id):
     with app.app_context():
          friend_of = db.session.query(friends_table).filter_by(user_id = user1_id, friend_id = user2_id).first()   
          friend_to= db.session.query(friends_table).filter_by(user_id = user2_id, friend_id = user1_id).first()  
          return  friend_of is not None  or friend_to is not None      
