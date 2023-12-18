from flask import *
from werkzeug.utils import secure_filename
import os
import secrets
import uuid
import time

from model.load import *
from helperFunctions.chatBOT import *
from helperFunctions.productScrape import *


UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])


import sqlite3

if os.path.exists("database.db"):
    os.remove("database.db")
conn = sqlite3.connect('database.db')
conn.execute('CREATE TABLE tokens (token TEXT, Imgpath TEXT, class TEXT)')
conn.close()



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

    with sqlite3.connect("database.db") as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("SELECT Imgpath FROM tokens WHERE token = ?",(str(cookieVal),))

        row = cur.fetchone()
        if row is None:
            pass
        else:
            ImgpathUser = row['Imgpath']
        parameterProduct = predict(ImgpathUser)
        con.execute("UPDATE tokens SET class = ? WHERE token = ?",(parameterProduct,str(cookieVal),))
        
    print("[+] ==>",parameterProduct)

    products = scrape_products(parameterProduct)
    if products != None:
        return render_template("getRecommendation.html",products=products)

@app.route("/wish2",methods=['GET','POST'])
def wish2():
    if request.method == 'POST':
        cookieVal = request.cookies.get('unique_cookie')
        query = request.form.get("query")

        with sqlite3.connect("database.db") as con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute("SELECT class FROM tokens WHERE token = ?",(str(cookieVal),))

            row = cur.fetchone()
            if row is None:
                pass
            else:
                imgClass = row['class']

        products = scrape_products(query + " " + imgClass.split(" ")[1])
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
                    cur.execute("INSERT INTO tokens (token,Imgpath,class) VALUES (?,?,?)",(unique_cookie_value,str(full_Path),"None"))
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
