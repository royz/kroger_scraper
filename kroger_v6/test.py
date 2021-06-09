import os
import json
import requests
from pprint import pprint


def get_cookies():
    if not os.path.exists('cookies.json'):
        print('cookies.json not found')
        quit()

    with open('cookies.json') as f:
        data = json.load(f)

    cookies = {}
    for row in data:
        cookies.update({row['name']: row['value']})

    return cookies


def get_upc(product_name):
    headers = {
        'authority': 'www.kroger.com',
        'accept': 'application/json, text/plain, */*',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/86.0.4240.198 Safari/537.36',
    }

    params = {
        'filter.locationId': '03400744',
        'filter.query': product_name,
    }

    response = requests.get('https://www.kroger.com/atlas/v1/search/v1/products-search',
                            headers=headers, params=params)
    try:
        return response.json()['data']['productsSearch'][0]['upc']
    except:
        return None


def get_aisle(location="03400744"):
    headers = {
        'authority': 'www.kroger.com',
        'accept': 'application/json, text/plain, */*',
        'x-modality': json.dumps({
            "modalityTypes": "PICKUP,SHIP",
            "locationId": location,
            "shipLatLng": "29.52947425842285,-95.201416015625",
            "shipPostalCode": "77546"
        }),
        'dnt': '1',
        'x-ship': 'true',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/86.0.4240.198 Safari/537.36',
        'content-type': 'application/json;charset=UTF-8',
        'origin': 'https://www.kroger.com',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://www.kroger.com/shopping/list/',
        'accept-language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,sv;q=0.6',
    }

    data = {
        "upcs": ["0002259205302", "0000000004011"],
        "filterBadProducts": True,
        "clicklistProductsOnly": True,
        "pathname": "/shopping/list/",
        "href": "https://www.kroger.com/shopping/list/",
        "shouldFetchAisleLocation": True,
        "shouldFetchNutritionInfo": False
    }

    response = requests.post('https://www.kroger.com/products/api/products/details',
                             headers=headers, cookies=get_cookies(), json=data)

    try:
        products = response.json()['products']
    except:
        return None

    aisles = []
    for product in products:
        try:
            aisle = product['location']['locations'][0]['aisle']['description']
            if aisle.lower().startswith('aisle'):
                aisle = aisle[5:].strip()
            aisles.append([product['upc'], aisle])
            # aisles.append([self.product_name(item['itemId']), aisle])
        except:
            pass
    return aisles


get_aisle('03400744')
