import secrets, os
from PIL import Image, ImageOps
from flask import render_template, url_for, flash, redirect, request, abort
from flaskblog import app, db, bcrypt, mail
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, RequestResetForm, ResetPasswordForm
from flaskblog.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message


@app.route("/")
@app.route("/home")
def home():

    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('home.html', posts=posts)


@app.route("/about")
def about():

    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():

    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = RegistrationForm()

    if form.validate_on_submit():

        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)

        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash(f'Your account has been successfully created!', 'success')

        return redirect(url_for('home'))

    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()

    if form.validate_on_submit():

        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):

            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash(f'You are logged in!', 'success')

            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for('home'))

        else:
            flash(f'Login unsuccessful. Please check your email and/or password', 'danger')

    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():

    logout_user()
    return redirect(url_for('login'))


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():

    form = UpdateAccountForm()

    if form.validate_on_submit():

        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        
        if form.default_picture.data:
            current_user.image_file = 'default.jpg'
        
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash(f'Your account has been updated!', 'success')

        return redirect(url_for('account'))

    elif request.method == 'GET':
        
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)

def save_picture(form_picture):

    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    f_name = random_hex + f_ext
    path = os.path.join(app.root_path, 'static/profile_pics', f_name)

    output_size = 125, 125
    image = Image.open(form_picture)
    image = ImageOps.exif_transpose(image)
    image.thumbnail(output_size)
    image.save(path)

    return f_name


@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():

    form = PostForm()

    if form.validate_on_submit():

        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash(f'Your post has been created!', 'success')

        return redirect(url_for('home'))

    return render_template('create_update_post.html', title='New Post', form=form, legend='New Post')


@app.route("/post/<int:post_id>")
def post(post_id):

    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):

    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data

        db.session.commit()
        flash(f'Your post has been updated!', 'success')

        return redirect(url_for('post', post_id=post.id))

    elif request.method == 'GET':

        form.title.data = post.title
        form.content.data = post.content

    return render_template('create_update_post.html', title='Update Post', form=form, legend='Update Post')


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):

    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)

    db.session.delete(post)
    db.session.commit()
    flash(f'Your post has been deleted!', 'success')

    return redirect(url_for('home'))


@app.route("/user/<string:username>")
def user_posts(username):

    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()

    posts = Post.query.filter_by(author=user)\
            .order_by(Post.date_posted.desc())\
            .paginate(page=page, per_page=5)

    return render_template('user_posts.html', posts=posts, user=user)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():

    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RequestResetForm()

    if form.validate_on_submit():
        
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash(f'An email has been sent to { form.email.data } with a link to reset your password', 'info')

        return redirect(url_for('login'))

    return render_template('reset_request.html', title='Reset Password', form=form)

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Flask Blog - Password Reset Request', sender='michiel.peeraer@telenet.be', recipients=[user.email])

    msg1 = f'To reset your password, click on the following link:\n\n'
    link = url_for('reset_password', token=token, _external=True)
    msg2 = f'\n\nIf you did not make this request, then simply ignore this email and no changes will be made.'

    msg.body = msg1 + link + msg2
    mail.send(msg)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_password(token):

    if current_user.is_authenticated:
        return redirect(url_for('home'))

    user = User.verify_reset_token(token)

    if user is None:
        flash(f'That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))

    form = ResetPasswordForm()

    if form.validate_on_submit():

        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()

        login_user(user)
        flash(f'Your password has been reset!', 'success')

        return redirect(url_for('home'))

    return render_template('reset_password.html', title='Reset Password', form=form)















# TO DO
#
# write function to choose/delete uploaded profile pic(s)
# translate website to english (everything, also error messages etc)
# working 'remember me'
# option to delete account