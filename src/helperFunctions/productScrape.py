from bs4 import BeautifulSoup
import urllib
import requests

def DecoreGlance(search_query="bedroom lamps"):

    base_url = 'https://decorglance.com/search?q={}'.format(urllib.parse.quote(search_query, safe=''))
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    try:
        with requests.Session() as session:
            session.get("https://decorglance.com/", headers=headers)

            response = session.get(base_url, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')

            products = []
            for product_card in soup.find_all('a',class_='grid-item__link'):
                name = product_card.find('div', class_='grid-product__title').text.strip()
                price = product_card.find('span', class_='grid-product__price--current').text.strip().split("\n")[0]
                image = 'http:' + product_card.find('img', class_='grid-product__image').get('data-src')
                link = product_card['href']
                products.append({
                    'name': name,
                    'price': price.replace("₹. ","₹ "),
                    'image': image.replace("_{width}x","").split("?")[0],
                    'link': 'https://decorglance.com' + link
                })

        return products
    except :
        return None

def IndianCircus(search_query="bedroom lamps"):

    base_url = 'https://indiacircus.com/icsearch/?q={}'.format(urllib.parse.quote(search_query, safe=''))
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    try:
        with requests.Session() as session:
            session.get("https://indiacircus.com/", headers=headers)

            response = session.get(base_url, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')

            products = []
            for product_card in soup.find_all('div', class_='product-wrap'):
                name = product_card.find('h4', class_='pro-title').find('a').text.strip()
                price = product_card.find('div', class_='pricebox').find('div', class_='sub').text.strip()
                image = product_card.find('div', class_='shop-image').find('img')['src']
                link = product_card.find('a', class_='product-item-photo')['href']
                products.append({
                    'name': name,
                    'price': price.replace("Rs.","₹ "),
                    'image': image,
                    'link': link
                })

        return products
    except:
        return None

def Pepperfry(search_query="bedroom lamps"):
    base_url = 'https://www.pepperfry.com/site_product/search?q={}'.format(urllib.parse.quote(search_query,safe=''))
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    try:
        response = requests.get(base_url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')

        products = []
        for product_card in soup.find_all('div', class_='product-card'):
            name = product_card.find('h3', class_='product-name').text.strip()
            price = product_card.find('span', class_='product-offer-price').text.strip()
            image = product_card.find('img')['src']
        # link
            link = product_card.find('a')['href']
            products.append({
                'name': name,
                'price': price.replace("₹","₹ "),
                'image': image,
                'link': 'https://www.pepperfry.com'+link
            })

        return products
    except:
        return None

def scrape_products(search_query="bedroom lamps"):
    a = Pepperfry(search_query)
    b = IndianCircus(search_query)
    c = DecoreGlance(search_query)

    result = []

    if a is not None:
        result.extend(a)
    if b is not None:
        result.extend(b)
    if c is not None:
        result.extend(c)

    return result if result else None
    
