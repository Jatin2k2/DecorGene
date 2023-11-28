from flask import *
from werkzeug.utils import secure_filename
import os
import secrets
import uuid
import time

import sqlite3

if os.path.exists("database.db"):
    os.remove("database.db")
conn = sqlite3.connect('database.db')
conn.execute('CREATE TABLE tokens (token TEXT, Imgpath TEXT)')
conn.close()

from model.load import *
from helperFunctions.chatBOT import *
from helperFunctions.productScrape import *


UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
classes_ML = [
    "natural_bedroom",
    "natural_dining_room",
    "natural_kitchen",
    "natural_living_room",
    "natural_bathroom",
    "classic_bedroom",
    "classic_dining_room",
    "classic_kitchen",
    "classic_living_room",
    "classic_bathroom",
    "casual_bedroom",
    "casual_dining_room",
    "casual_kitchen",
    "casual_living_room",
    "casual_bathroom",
    "modern_bedroom",
    "modern_dining_room",
    "modern_kitchen",
    "modern_living_room",
    "modern_bathroom"
]

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.debug = True
app.jinja_env.auto_reload = True
app.secret_key = secrets.token_hex(16)



@app.route("/get", methods=["GET", "POST"])
def chat():
    msg = request.form["msg"]
    input = msg
    return get_Chat_response(input)

@app.route('/uploads/<path:name>')
def uploads(name):
    return send_from_directory(app.config['UPLOAD_FOLDER'],name)

@app.route("/wishes")
def wishes():
    return render_template("wishes.html")

@app.route("/getRecommendation")
def getRecommendation():

    cookieVal = request.cookies.get('unique_cookie')
    con = sqlite3.connect("database.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT Imgpath FROM tokens WHERE token = ?",(str(cookieVal),))
    row = cur.fetchone()
    if row is None:
        pass
    else:
        ImgpathUser = row['Imgpath']

    imageClass = predict(ImgpathUser)
    parameterProduct = classes_ML[imageClass].replace("_"," ").replace("-"," ")
    print("[+] ==>",parameterProduct)
    products = scrape_products(parameterProduct)
    return render_template("getRecommendation.html",products=products)

@app.route("/wish2",methods=['GET','POST'])
def wish2():
    if request.method == 'POST':
        query = request.form.get("query")
        products = scrape_products(query)
        response = make_response(render_template("wish2.html",products=products))
        response.headers["Cache-Control"] = "no-store"
        return response
    else:
        response = make_response(render_template("wish2.html"))
        response.headers["Cache-Control"] = "no-store"
        return response


@app.route("/theGenie")
def theGenie():
    return render_template("theGenie.html")

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
            return redirect(url_for('/'))
    
        file = request.files['file']
        if file.filename == '':
            flash('No File Selected',category='error')
            return redirect(url_for('/'))

    
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            filename = str(time.time()) + "_" + filename

            upload_folder = app.config['UPLOAD_FOLDER']
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            try:
                full_Path = os.path.join(upload_folder,filename)
                file.save(full_Path)
                unique_cookie_value = str(uuid.uuid4())

                with sqlite3.connect("database.db") as con:
                    cur = con.cursor()
                    cur.execute("INSERT INTO tokens (token,Imgpath) VALUES (?,?)",(unique_cookie_value,str(full_Path)))
                    con.commit()
                res = make_response(redirect(url_for('wishes')))
                res.set_cookie('unique_cookie', unique_cookie_value)
                return res

            except Exception as e:
                flash('Internal Error',category='error')
                return redirect(url_for('/'))
    else:
        return render_template('home.html')



if __name__ == '__main__':
    app.run()
