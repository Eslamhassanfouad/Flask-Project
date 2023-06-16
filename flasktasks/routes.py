from sqlite3 import IntegrityError
from flask import render_template, redirect, url_for, flash,request
import sqlalchemy
from flasktasks import app , forms,db, bcrypt , login_manager
from flasktasks.models import User
from flask_login import current_user, login_user, logout_user, login_required

nav_items = [
    {'name': 'Home', 'url': '/home'},
    {'name': 'About', 'url': '/about'},
    {'name': 'Register', 'url': '/register'},
    {'name': 'Login', 'url': '/login'}


]
users = [
    {'email': 'test@example.com',
     'password1':'12345678',
      },
     {'email': 'test2@example.com',
     'password1':'12345678',
      },
]


    

@app.route('/home')
def home_endpoint():
    return render_template('home.html' , nav_items=nav_items)

@app.route('/about')
def about_endpoint():
    return render_template('about.html', nav_items=nav_items)

@app.route('/register' , methods=['POST','GET'])
def register_endpoint():
    register_form = forms.RegisterForm()
    if register_form.validate_on_submit():
        try:
                  with app.app_context():
                            hashed_pw = bcrypt.generate_password_hash(register_form.password1.data).decode('utf-8')
                            new_user = User(
                                name=register_form.name.data,
                                email=register_form.email.data,
                                password=hashed_pw
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

