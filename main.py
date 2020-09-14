from flask import *
import dataset
from io import BytesIO
import random
import string

from salt import hash

app = Flask('Neverland')
app.secret_key = 'mwz!R&n$%Fh*TBHkk@Ksare=vjkRQ4Xmz%fCm=yFGsDfyZA^T97%JWXtp^3#C+Y*g&eJdx9crb4^7_BWNxt4sZYJ_4NFmLJ2%s3U+@%*_-py5z3VQ?$m^X8y?j?jaN^*'
file_db = dataset.connect('sqlite:///file_database.db')
user_db = dataset.connect('sqlite:///user_database.db')

@app.before_request
def before_request():
    g.user = None

    if 'token' in session:
        if user_db['users'].find_one(token=session['token'])['ip'] == request.remote_addr:
            g.user = user_db['users'].find_one(token=session['token'])['name']
        else:
            user_db['users'].update(dict(name=user_db['users'].find_one(token=session['token'])['name'], token=''), ['name'])
            session.pop('token', None)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        session.pop('token', None)
        username = request.form['uname']
        password = request.form['pwd']

        if found_user := user_db['users'].find_one(name=username):
            if hash(password) == found_user['password']:
                token = ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=64))
                user_db['users'].update(dict(name=username, token=token), ['name'])
                user_db['users'].update(dict(name=username, ip=request.remote_addr), ['name'])
                session['token'] = token
                return redirect(url_for('index'))
        
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/')
def index():
    if not g.user:
        return redirect(url_for('login'))
    
    return render_template('index.html', files=file_db['files'])

@app.route('/upload', methods=['POST'])
def upload():
    if not g.user:
        return redirect(url_for('login'))
    
    file = request.files['inputFile']
    if file.filename != '' and file_db['files'].find_one(name=str(file.filename)) is None:
        file_db['files'].insert(dict(name=file.filename, data=file.read()))

    return redirect(url_for('index'))

@app.route('/download/<filename>')
def download(filename):
    if not g.user:
        return redirect(url_for('login'))
    
    return send_file( BytesIO(file_db['files'].find_one(name=str(filename))['data']), attachment_filename=str(filename), as_attachment=True)