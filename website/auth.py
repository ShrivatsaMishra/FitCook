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

@auth.route('/chef_signup')
def chef_signup():
    return render_template("chef_signup.html")

@auth.route('/delivery_signup')
def delivery_signup():
    return render_template("delivery_signup.html")

@auth.route('/manager_signup')
def manager_signup():
    return render_template("manager_signup.html")

@auth.route('/publicity_signup')
def publicity_signup():
    return render_template("publicity_signup.html")