import requests
from bs4 import BeautifulSoup
import pandas as pd
import re


base_url = "https://online.metro-cc.ru/category/myasnye/kolbasy-vetchina?from=under_search&page="
data = []
home_url = "https://online.metro-cc.ru"

def find_brand(text):
    pattern2 = r'\b[А-ЯЁ][а-яё]*\b|\b[а-яё]{2,}\b'
    pattern = r'\b[a-zA-Z]+\b'

    matches = re.finditer(pattern, text)
    serch_brend = next(matches, None)

    if serch_brend != None:
        serch_brend = serch_brend.group()
    else:
        matches = re.finditer(pattern2, text)
        words = [match.group() for match in matches]
        second_word = [x for x in words if x[0].isupper()]
        serch_brend = second_word[1]

    return serch_brend

def take_price(data):
    # promo_price = re.findall('\d+', promo_price)
    # promo_price = ''.join(promo_price) if isinstance(promo_price, list) \
    #     and (isinstance(x, str) for x in promo_price) else promo_price
    
    data = re.sub(r'[^\d.]', '', data)
    parts = data.split('.')
    if len(parts) == 2:
        whole, fractional = parts
    else:
        whole = parts[0]
        fractional = ''

    whole = whole.replace('.', '')
    
    return whole + '.' + fractional if fractional else whole

for page in range(1,2):
    url = f"{base_url}{page}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    products = soup.find("div", id="products-inner")
    
    for product in products:
        # for pro in product:
        if product != ' ':
            id = int(product.attrs['id'])
            name = product.find("span", class_="product-card-name__text").text.strip()
            link = product.find("a", class_="product-card-name reset-link catalog-2-level-product-card__name style--catalog-2-level-product-card")["href"]
            link = f"{home_url}{link}"
            try:
                promo_price = product.find("div", class_="product-unit-prices__actual-wrapper").text.strip()
                promo_price = take_price(promo_price)
            except AttributeError:
                promo_price = None
            try:
                regular_price = product.find("span", class_="product-price nowrap product-unit-prices__old style--catalog-2-level-product-card-major-old").text.strip()
                regular_price = take_price(regular_price)
            except AttributeError:
                regular_price = promo_price if promo_price != None else None 
            
            brand = find_brand(name)
            
            data.append({
                "id": id,
                "name": name,
                "link": link,
                "regular_price": regular_price,
                "promo_price": promo_price,
                "brand": brand
            })


# print(response.status_code )
# «navigator.userAgent
df = pd.DataFrame(data)
df.to_csv("metro_products.csv", index=False)