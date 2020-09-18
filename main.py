import random
import string
import os
import secrets

from salt import hash_my_ass

from flask import (
    Flask,
    request,
    g,
    render_template,
    session,
    redirect,
    url_for,
    send_file
)
import dataset
import humanize

app = Flask('neverland')
app.config['UPLOAD_FOLDER'] = 'files'
app.secret_key = 'mwz!R&n$%Fh*TBHkk@Ksare=vjkRQ4Xmz%fCm=yFGsDfyZA^T97%JWXtp^3#C+Y*g&eJdx9crb4^7_BWNxt4sZYJ_4NFmLJ2%s3U+@%*_-py5z3VQ?$m^X8y?j?jaN^*'

user_db = dataset.connect('sqlite:///user_database.db')
file_db = dataset.connect('sqlite:///file_database.db')

@app.before_request
def before_request():
    g.user = None

    if 'token' in session:
        if user_db['users'].find_one(token=session['token']) is None:
            session.pop('token', None)
        else:
            if user_db['users'].find_one(token=session['token'])['ip'] == request.remote_addr:
                g.user = user_db['users'].find_one(token=session['token'])['name']
            else:
                user_db['users'].update(dict(name=user_db['users'].find_one(token=session['token'])['name'], token=''), ['name'])
                session.pop('token', None)

@app.route('/')
def index():
    if not g.user:
        return redirect(url_for('login'))

    return render_template('index.html', files=file_db['files'] )

@app.route('/upload', methods=['POST'])
def upload():
    if not g.user:
        return redirect(url_for('login'))
    
    files = request.files.getlist('file-input')
    for file in files:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath) 

        file_db['files'].insert(dict(
            name=file.filename,
            path=filepath,
            size=humanize.naturalsize(os.stat(filepath).st_size),
            uploader=g.user
        ))

    return redirect(url_for('index'))

@app.route('/download/<filename>')
def download(filename: str):
    if not g.user:
        return redirect(url_for('login'))
    
    return send_file(file_db['files'].find_one(name=filename)['path'], attachment_filename=filename, as_attachment=True)

@app.route('/delete/<filename>')
def delete(filename: str):
    if not g.user:
        return redirect(url_for('login'))

    if file_db['files'].find_one(name=filename)['uploader'] != g.user:
        return redirect(url_for('index'))

    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    file_db['files'].delete(name=filename)

    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        session.pop('token', None)
        username = request.form['uname']
        password = request.form['pwd']

        if found_user := user_db['users'].find_one(name=username):
            if hash_my_ass(password) == found_user['password']:
                token = secrets.token_hex(32)
                user_db['users'].update(dict(name=username, token=token), ['name'])
                user_db['users'].update(dict(name=username, ip=request.remote_addr), ['name'])
                session['token'] = token
                return redirect(url_for('index'))
        
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('token', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if g.user:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form['uname']
        password = request.form['pwd']

        if user_db['users'].find_one(name=username) is not None or user_db['users_on_hold'].find_one(name=username) is not None:
            return redirect(url_for('register', taken='1'))

        user_db['users_on_hold'].insert(dict(
            name=username,
            password=hash_my_ass(password),
            ip=request.remote_addr
        ))

        return redirect(url_for('login'))


    return render_template('register.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not g.user:
        return redirect(url_for('index'))

    if user_db['users'].find_one(name=g.user)['admin'] != 'yes':
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        if 'approve' in request.form['submit-button']:
            name = request.form['submit-button'].split('?')[1]

            user = user_db['users_on_hold'].find_one(name=name)
            user_db['users'].insert(dict(
                name=user['name'],
                password=user['password'],
                token=' ',
                ip=user['ip'],
                admin='no'
            ))

            user_db['users_on_hold'].delete(name=name)
        elif 'deny' in request.form['submit-button']:
            name = request.form['submit-button'].split('?')[1]

            user_db['users_on_hold'].delete(name=name)

    return render_template('admin.html', users=user_db['users_on_hold'])