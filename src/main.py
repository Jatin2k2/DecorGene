from flask import *
from werkzeug.utils import secure_filename
import os
import secrets
import requests
from bs4 import BeautifulSoup

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.debug = True
app.jinja_env.auto_reload = True
app.secret_key = secrets.token_hex(16)


def scrape_products():#search_query):
    base_url = 'https://www.pepperfry.com/site_product/search?q=bedroom%20clock'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    #params = {'k': search_query}

    response = requests.get(base_url, headers=headers)#, params=params)
    print(response.status_code)
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



@app.route("/wishes")
def wishes():
    return render_template("wishes.html")

@app.route("/getRecommendation")
def getRecommendation():
    products = scrape_products()

    return render_template("getRecommendation.html",products=products)

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