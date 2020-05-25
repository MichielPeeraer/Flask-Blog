import os
import secrets
from PIL import Image, ImageOps
from flask import url_for, current_app
from flask_mail import Message
from flaskblog import mail

def save_picture(form_picture):

    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    f_name = random_hex + f_ext
    path = os.path.join(current_app.root_path, 'static/profile_pics', f_name)

    output_size = 125, 125
    image = Image.open(form_picture)
    image = ImageOps.exif_transpose(image)
    image.thumbnail(output_size)
    image.save(path)

    return f_name

def send_reset_email(user):

    token = user.get_reset_token()
    msg = Message('Flask Blog - Password Reset Request', sender='michiel.peeraer@telenet.be', recipients=[user.email])

    msg1 = f'To reset your password, click on the following link:\n\n'
    link = url_for('users.reset_password', token=token, _external=True)
    msg2 = f'\n\nIf you did not make this request, then simply ignore this email and no changes will be made.'

    msg.body = msg1 + link + msg2
    mail.send(msg)