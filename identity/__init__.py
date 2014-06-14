from __future__ import unicode_literals

import os
import logging
import bcrypt
import yaml
from logging.handlers import SMTPHandler
from flask import (
    Flask,
    g,
    make_response,
    redirect,
    render_template,
    request,
    session,
)
from werkzeug.exceptions import BadRequestKeyError
from openid.extensions import sreg
from openid.server import server
from openid.store.filestore import FileOpenIDStore

PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(PROJECT_ROOT, 'config.yml'), 'r') as fh:
    config = yaml.load(fh.read())

app = Flask(__name__, static_folder=os.path.join(PROJECT_ROOT, 'static'),
            static_url_path='/static')
app.secret_key = os.environ.get('SECRET_KEY')

store = FileOpenIDStore('sstore')
if 'SERVER_NAME' in os.environ:
    base_url = os.environ['SERVER_NAME']
else:
    port = os.environ.get('PORT', '5000')
    base_url = 'http://localhost:' + port + '/'

oidserver = server.Server(store, base_url + 'openidserver')

if 'EMAIL_PASSWORD' in os.environ and not app.debug:
    mail_handler = SMTPHandler('smtp.sendgrid.net',
                               config['error_email'],
                               [config['error_email']],
                               'Identity error',
                               (os.environ['EMAIL_USERNAME'],
                                os.environ['EMAIL_PASSWORD']))
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
    session['approved'] = session.get('approved', {})

@app.context_processor
def user_info():
    return {
        'name': config['name'],
        'compliment': config['preferred_compliment'],
    }

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html.jinja',
                           user=g.user,
                           redirect_url=request.args.get('redirect_url', '')
                           )

@app.route('/', methods=['POST'])
def login():
    passphrase = request.form['passphrase'].encode('utf-8')
    if bcrypt.hashpw(passphrase, config['password_digest']) \
            == config['password_digest']:
        session['user'] = config['name']

    redirect_url = request.form.get('redirect_url', '/')
    return redirect(redirect_url)

@app.route('/logout', methods=['GET'])
def logout():
    if 'user' in session:
        session.pop('user')
    return redirect('/')

@app.route('/openidserver', methods=['GET', 'POST'])
def server():
    query = request.args.copy()
    query.update(request.form)

    if 'user' not in session:
        session['attempted_query'] = query
        return redirect('/?redirect_url=%2Fopenidserver')
    if 'attempted_query' in session:
        query = session.pop('attempted_query')

    openid_request = oidserver.decodeRequest(query)
    if openid_request is None:
        return redirect('/')

    if openid_request.mode in ['checkid_immediate', 'checkid_setup']:
        is_authorized = False
        if g.user is not None and \
                openid_request.trust_root in session['approved']:
            is_authorized = True
        if is_authorized:
            return openid_request.answer(True)
        elif openid_request.immediate:
            return openid_request.answer(False)
        else:
            session['last_check_id_request'] = query
            return render_template('decide.html.jinja',
                                   trust_root=openid_request.trust_root)
    else:
        return render_response(oidserver.handleRequest(openid_request))


@app.route('/allow', methods=['POST'])
def allow():
    try:
        last_query = session.get('last_check_id_request')
    except KeyError as e:
        raise BadRequestKeyError(e.message)
    openid_request = oidserver.decodeRequest(last_query)
    if 'yes' in request.form:
        if request.form.get('remember', 'no') == 'yes':
            trust_root = openid_request.trust_root
            session['approved'][trust_root] = 'always'

        response = openid_request.answer(True, identity=base_url + 'id')
        sreg_request = sreg.SRegRequest.fromOpenIDRequest(openid_request)
        sreg_data = {
            'name': config['name'],
        }

        sreg_response = sreg.SRegResponse.extractResponse(
                sreg_request, sreg_data)
        response.addExtension(sreg_response)
    elif 'no' in request.form:
        response = openid_request.answer(False)
    else:
        raise BadRequestKeyError('strange allow post.')

    return render_response(response)

@app.route('/id')
def id():
    approved_trust_roots = session['approved'].keys()
    return render_template('id.html.jinja',
                           user=g.user,
                           approved_trust_roots=approved_trust_roots,
                           base_url=base_url,
                           )

def render_response(response):
    oidresponse = oidserver.encodeResponse(response)
    return make_response((oidresponse.body,
                          oidresponse.code,
                          oidresponse.headers))
