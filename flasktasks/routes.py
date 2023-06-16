from flask import render_template, redirect, url_for, flash
from flasktasks import app , forms
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
        user = {'email': register_form.email.data,
                'password1': register_form.password1.data}
        users.append(user)
        flash(f"Registration Successful for {register_form.email.data}!")
        return redirect(url_for('home_endpoint'))
    return render_template('register.html', data = {'form': register_form , 'nav_items': nav_items})

@app.route('/login' , methods=['POST','GET'])
def login_endpoint():
    flag = False
    login_form = forms.LoginForm()
    if login_form.validate_on_submit():
        for user in users:
            if user['email'] == login_form.email.data and user['password1'] == login_form.password.data:
                flag = True
                print('found user')
                break
        if flag == True:
                flash(f"Logging in Successful for {login_form.email.data}!")
                return redirect(url_for('home_endpoint'))
        else:   
                print("Login Failed")
                flash(f"Invalid email or password")
                return render_template('login.html', data = {'form': login_form , 'nav_items': nav_items})
                
    return render_template('login.html', data = {'form': login_form , 'nav_items': nav_items})




