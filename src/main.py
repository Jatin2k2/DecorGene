from flask import *
from werkzeug.utils import secure_filename
import os
import secrets

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.jinja_env.auto_reload = True
app.secret_key = secrets.token_hex(16)
"""
@app.route("/")
def home():
    return render_template("home.html")
"""

@app.route("/getRecommendation")
def getRecommendation():
    return render_template("getRecommendation.html")

@app.route("/about")
def about():
    return render_template("about.html")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/",methods=['GET','POST'])
def home():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No File part',category='error')
            return jsonify({'error': 'No File part'}), 400
    
        file = request.files['file']
        if file.filename == '':
            flash('No File Selected',category='error')
            return jsonify({'error': 'No File Selected'}), 400
    
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
        
            upload_folder = app.config['UPLOAD_FOLDER']
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            try:
                file.save(os.path.join(upload_folder,filename))
                flash('Uploaded',category='info')
                #return redirect(url_for('getRecommendation'))
                return jsonify({'message': 'Uploaded'}), 200
            except Exception as e:
                flash('Internal Error',category='error')
                return jsonify({'error': 'Internal Error'}), 500
    
    else:
        return render_template('home.html')



if __name__ == '__main__':
    app.run()