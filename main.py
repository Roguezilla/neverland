from flask import *
import dataset
from io import BytesIO

app = Flask('Neverland')
db = dataset.connect('sqlite:///file_database.db')

@app.route('/')
def index():
    return render_template('index.html', files=db['files'])

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['inputFile']
    if file.filename != '' and db['files'].find_one(name=str(file.filename)) is None:
        db['files'].insert(dict(name=file.filename, data=file.read()))

    return redirect(url_for('index'))

@app.route('/download/<filename>')
def download(filename):
    return send_file( BytesIO(db['files'].find_one(name=str(filename))['data']), attachment_filename=str(filename), as_attachment=True)