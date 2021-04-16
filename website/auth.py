from flask import Blueprint, render_template

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template("login.html")

@auth.route('/logout')
def logout():
    return "<h2>Log Out</h2>"


@auth.route('/signup')
def signup():
    return render_template("signup.html")

@auth.route('/customer_signup')
def custumer_signup():
    return render_template("customer_signup.html")