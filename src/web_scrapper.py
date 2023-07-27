import requests
from bs4 import BeautifulSoup

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

#print(scrape_amazon_products())#'Modern Bedroom'))
