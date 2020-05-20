from flask import render_template, url_for, flash, redirect
from flaskblog import app
from flaskblog.forms import RegistrationForm, LoginForm
from flaskblog.models import User, Post

posts = [
    {
        'author': 'J.K. Rowling',
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'May 18, 2020'
    },
    {
        'author': 'Stephen King',
        'title': 'Blog Post 2',
        'content': 'Second post content',
        'date_posted': 'May 19, 2020'
    }
]

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', posts=posts)

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        flash(f'{form.username.data}, your account has been successfully created!', 'success')
        return redirect(url_for('home'))

    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        if form.email.data == 'test@test.test' and form.password.data == 'test':
            flash(f'You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash(f'Login unsuccessful. Please check your username and/or password', 'danger')

    return render_template('login.html', title='Login', form=form)

@app.route("/about")
def about():
    return render_template('about.html', title='About')