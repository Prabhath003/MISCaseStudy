"""
This file contains the routes for the authentication blueprint.

The blueprint is responsible for handling all routes related to user authentication, including login, logout, and sign up.

The routes are defined using the Flask 'route' decorator. The decorator takes two arguments: the URL pattern and a list of HTTP methods.

Within the function, the request data is retrieved using the 'request.form' method, which returns a dictionary of form data. The data is then validated using a series of if statements that check for valid input. If the input is valid, the user is authenticated using the 'login_user' function from the 'flask_login' module.

Once authenticated, the user is redirected to the homepage. If the user attempts to access a restricted page without being authenticated, they will be redirected to the login page.

The 'sign_up' route is similar, but it also includes additional validation steps to ensure that the user provides valid input. If the input is valid, a new user is created using the 'User' model, and the 'login_user' function is used to authenticate the user.

The 'logout' route simply logs out the user by calling the 'logout_user' function.
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user

from .models import User
from . import db

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    This function handles the login route.

    If the request method is 'POST', the form data is retrieved using the 'request.form' method, and the email and password are extracted. The 'User' model is then used to query for a user with the specified email.

    If the user exists, the password is checked using the 'check_password_hash' function from the 'werkzeug.security' module. If the passwords match, the user is authenticated using the 'login_user' function from the 'flask_login' module.

    A message is then flashed to the user, and they are redirected to the homepage. If the passwords do not match, or the user does not exist, an error message is flashed.

    If the request method is 'GET', the login form is rendered.

    :return: a rendered login template
    """
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user:
            if check_password_hash(user.password, password):
                flash('Logged in succesfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('tasks.home'))
            else:
                flash('Invalid email or password', category='error')
        else:
            flash('Email does not exit.', category='error')
    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    """
    This function handles the logout route.

    It simply logs out the user by calling the 'logout_user' function from the 'flask_login' module.

    :return: a redirect to the login page
    """
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    """
    This function handles the sign up route.

    If the request method is 'POST', the form data is retrieved using the 'request.form' method, and the email, first name, role, password1, and password2 are extracted. The 'User' model is then used to query for a user with the specified email.

    If the user exists, an error message is flashed.

    If the email is less than 4 characters long, an error message is flashed.

    If the first name is less than 2 characters long, an error message is flashed.

    If the role is less than 2 characters long, an error message is flashed.

    If the passwords do not match, an error message is flashed.

    If the password is less than 7 characters long, an error message is flashed.

    If no errors are encountered, a new user is created using the 'User' model, the passwords are hashed using the 'generate_password_hash' function from the 'werkzeug.security' module, and the 'login_user' function is used to authenticate the user.

    A message is then flashed to the user, and they are redirected to the homepage.

    If the request method is 'GET', the sign up form is rendered.

    :return: a rendered sign up template
    """
    if request.method == 'POST':
        email = request.form.get('email')
        firstName = request.form.get('firstName')
        role = request.form.get('role')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif email and len(email) < 4:
            flash('Invalid Email', category='error')
        elif firstName and len(firstName) < 2:
            flash('First name must be greater than 1 characters', category='error')
        elif role and len(role) <= 1:
            flash('Please Enter your role', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match', category='error')
        elif password1 and len(password1) < 7:
            flash('Password must be atleast 7 characters.', category='error')
        else:
            new_user = User(email=email, first_name=firstName, role=role, password=generate_password_hash(password1))
            db.session.add(new_user)
            
            db.session.commit()

            login_user(new_user, remember=True)

            flash('Account created!', category='success')
            return redirect(url_for('tasks.home'))

    return render_template("signup.html", user=current_user)