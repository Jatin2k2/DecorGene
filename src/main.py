from flask import *
from werkzeug.utils import secure_filename
import os
import secrets
import requests
from bs4 import BeautifulSoup
import base64
import urllib
import uuid
from flask import make_response

from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from keras.models import model_from_json
from tensorflow.keras.applications.vgg16 import preprocess_input
import json
import numpy as np


import sqlite3
conn = sqlite3.connect('database.db')
conn.execute('CREATE TABLE tokens (token TEXT, Imgpath TEXT)')
conn.close()




with open('C:\\Users\\amrit\\Documents\\CapStone\\DecorGene\\src\\model\\model.json', 'r') as f:
    model_json = f.read()

MLmodel = model_from_json(model_json)
MLmodel.load_weights("C:\\Users\\amrit\\Documents\\CapStone\\DecorGene\\src\\model\\interior_design_model.h5")
MLmodel.compile(optimizer=Adam(lr=0.00001), loss='categorical_crossentropy', metrics=['accuracy'])



tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")

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


def get_Chat_response(text):

    # Let's chat for 5 lines
    for step in range(5):
        # encode the new user input, add the eos_token and return a tensor in Pytorch
        new_user_input_ids = tokenizer.encode(str(text) + tokenizer.eos_token, return_tensors='pt')

        # append the new user input tokens to the chat history
        bot_input_ids = torch.cat([chat_history_ids, new_user_input_ids], dim=-1) if step > 0 else new_user_input_ids

        # generated a response while limiting the total chat history to 1000 tokens, 
        chat_history_ids = model.generate(bot_input_ids, max_length=1000, pad_token_id=tokenizer.eos_token_id)

        # pretty print last ouput tokens from bot
        return tokenizer.decode(chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)



def scrape_products(search_query="bedroom lamps"):
    base_url = 'https://www.pepperfry.com/site_product/search?q={}'.format(urllib.parse.quote(search_query,safe=''))
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    response = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    products = []
    for product_card in soup.find_all('div', class_='product-card'):
        name = product_card.find('h3', class_='product-name').text.strip()
        price = product_card.find('span', class_='product-offer-price').text.strip()
        image = product_card.find('img')['src']

        products.append({
            'name': name,
            'price': price,
            'image': image
        })

    return products


def predict(img_path):
    image = load_img(img_path, target_size=(224, 224))
    image_data = img_to_array(image)
    preprocessed_image_data = np.expand_dims(image_data, axis=0)
    preprocessed_image_data = preprocess_input(preprocessed_image_data)
    prediction = MLmodel.predict(preprocessed_image_data)
    class_label = np.argmax(prediction)
    return class_label


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
