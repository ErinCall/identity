from __future__ import unicode_literals

import os
import logging
import bcrypt
from logging.handlers import SMTPHandler
from flask import Flask, render_template, g, request, session, redirect

PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
app = Flask(__name__, static_folder=os.path.join(PROJECT_ROOT, 'static'),
            static_url_path='/static')
app.secret_key = os.environ.get('SECRET_KEY')

if 'SENDGRID_PASSWORD' in os.environ and not app.debug:
    mail_handler = SMTPHandler('smtp.sendgrid.net',
                               'identity-errors@andrewlorente.com',
                               ['identity-errors@andrewlorente.com'],
                               'Identity error',
                               (os.environ['SENDGRID_USERNAME'], os.environ['SENDGRID_PASSWORD']))
    mail_handler.setLevel(logging.ERROR)
    mail_handler.setFormatter(logging.Formatter('''
Message type:       %(levelname)s
Location:           %(pathname)s:%(lineno)d
Module:             %(module)s
Function:           %(funcName)s
Time:               %(asctime)s

Message:

%(message)s
'''))
    app.logger.addHandler(mail_handler)

@app.before_request
def before_request():
    g.user = getattr(g, 'user', session.get('user', None))

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html.jinja', user=g.user)

@app.route('/', methods=['POST'])
def login():
    my_hashed_password = b"$2a$10$XcUFtgOUkAAZdNH7tkcMqOwE6Mrn00dcVHcqVxUCEHgO683ygxEsC"
    passphrase = request.form['passphrase'].encode('utf-8')
    if bcrypt.hashpw(passphrase, my_hashed_password) == my_hashed_password:
        session['user'] = 'Andrew'
    return redirect('/')
