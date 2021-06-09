# encoding: utf-8

import os
import csv
import json
import pprint
import requests
from json.decoder import JSONDecodeError


class Kroger:
    def __init__(self):
        self.errors = 0
        self.store_ids = []  # id of the stores which are already found in previous searches or cache
        self.stores = []  # a list of all the stores found with their details
        self.cached_products = {}  # dictionary of the products which are cached
        self.upcs = []  # upc of the searched products
        self.all_product_upcs = {}
        self.cookies = self.get_cookies()  # cookies from cookies.txt
        self.products = self.get_product_names()  # product names from input/products.csv
        self.zip_codes = self.get_zip_codes()  # zip codes from input/zip-codes.csv
        self.cached_stores = self.get_cached_stores()  # store_id details found in site_cache/stores.csv if exists
        self.cached_upcs = self.get_cached_products()  # upc of the products stored in site_cache/upc.csv

    @staticmethod
    def get_product_names():
        if not os.path.exists('input/products.csv'):
            print('products.csv not found in input folder')
            quit()

        with open('input/products.csv', encoding='utf-8') as f:
            return f.read().strip().split('\n')

    @staticmethod
    def get_zip_codes():
        if not os.path.exists('input/zip-codes.csv'):
            print('zip-codes.csv not found in input folder')
            quit()

        with open('input/zip-codes.csv', encoding='utf-8') as f:
            zip_codes = f.read().strip().split('\n')
        return ['0' * (5 - len(zip_code)) + zip_code for zip_code in zip_codes]

    @staticmethod
    def get_cookies():
        if not os.path.exists('cookies.txt'):
            print('cookies.txt not found')
            quit()

        with open('cookies.txt') as f:
            data = json.loads(f.read().strip())

        cookies = {}
        for row in data:
            cookies.update({row['name']: row['value']})
        try:
            cookies['XSRF-TOKEN']
        except KeyError:
            print('XSRF-TOKEN not found in cookies')
            print('please update the cookies and try again...')
            quit()
        return cookies

    def product_name(self, upc):
        return self.all_product_upcs[upc]

    def get_cached_products(self):
        if not os.path.exists('site_cache/upc.csv'):
            return []
        with open('site_cache/upc.csv') as f:
            reader = csv.reader(f)
            try:
                next(reader)
            except StopIteration:
                return []
            upcs = list(reader)
            self.cached_products = {product[0]: product[1] for product in upcs}
            return upcs

    @staticmethod
    def get_cached_stores():
        if not os.path.exists('site_cache/stores.csv'):
            return []

        with open('site_cache/stores.csv') as f:
            reader = csv.reader(f)
            try:
                next(reader)
                stores = list(reader)
            except StopIteration:
                return []

        # if len(stores) > 0:
        #     print(f'found {len(stores)} store_id data in cache')
        # self.store_ids = [store_id[2] + store_id[3] for store_id in stores]
        return stores

    def get_all_product_upcs(self):
        for product in self.upcs + self.cached_upcs:
            self.all_product_upcs[product[1]] = product[0]

    def search_stores(self, zip_code):
        print(zip_code, ': ', end='')

        headers = {
            'authority': 'www.kroger.com',
            'origin': 'https://www.kroger.com',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36',
            'content-type': 'application/json;charset=UTF-8',
            'accept': 'application/json, text/plain, */*',
            'dnt': '1',
            'sec_req_type': 'ajax',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'referer': 'https://www.kroger.com/stores/search?searchText=00617',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9,bn;q=0.8',
        }

        data = {
            'operationName': 'storeSearch',
            'query': "↵      query storeSearch($searchText: String!, $filters: [String]!) {↵        storeSearch(searchText: $searchText, filters: $filters) {↵          stores {↵            ...storeSearchResult↵          }↵          fuel {↵            ...storeSearchResult↵          }↵          shouldShowFuelMessage↵        }↵      }↵      ↵  fragment storeSearchResult on Store {↵    banner↵    vanityName↵    divisionNumber↵    storeNumber↵    phoneNumber↵    showWeeklyAd↵    showShopThisStoreAndPreferredStoreButtons↵    storeType↵    distance↵    latitude↵    longitude↵    tz↵    ungroupedFormattedHours {↵      displayName↵      displayHours↵      isToday↵    }↵    address {↵      addressLine1↵      addressLine2↵      city↵      countryCode↵      stateCode↵      zip↵    }↵    pharmacy {↵      phoneNumber↵    }↵    departments {↵      code↵    }↵    fulfillmentMethods{↵      hasPickup↵      hasDelivery↵    }↵  }↵",
            'variables': {'searchText': zip_code, 'filters': []}
        }
        try:
            response = requests.post('https://www.kroger.com/stores/api/graphql', headers=headers, json=data)
            data = response.json()
            stores = data['data']['storeSearch']['stores']
        except:
            print('failed to get results')
            return
        stores_data = []
        for store in stores:
            store_id = store['divisionNumber'] + store['storeNumber']
            if store_id in self.store_ids:
                continue
            else:
                self.store_ids.append(store_id)
            stores_data.append({
                'banner': store['banner'],
                'divisionNumber': store['divisionNumber'],
                'storeNumber': store['storeNumber'],
                'latitude': store['latitude'],
                'longitude': store['longitude'],
                'address': store['address']['addressLine1'],
                'zip': store['address']['zip'],
                'searched_zip': zip_code
            })
        print(f'found {len(stores)} stores. {len(stores_data)} new')
        self.stores.extend(stores_data)

    def find_upc(self, product):
        if product in self.cached_products:
            # print(product, ':', self.cached_products[product])
            return

        headers = {
            'origin': 'https://www.kroger.com',
            'x-division-id': '034',
            'x-store_id-id': '00346',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36',
        }

        params = {
            'start': '0',
            'count': '20',
            'query': product,
            'tab': '0',
            'fulfillment': 'csp',
            'sth': 'true',
            'monet': 'true'
        }

        response = requests.get('https://www.kroger.com/search/api/searchAll', headers=headers, params=params)

        try:
            print(f'{product} : {response.json()["upcs"][0]}')
            self.upcs.append([product, response.json()['upcs'][0]])
        except IndexError:
            print(product, ': Not Found')

    def get_aisle_numbers(self, division, store, upcs):
        headers = {
            'authority': 'www.kroger.com',
            'origin': 'https://www.kroger.com',
            'x-xsrf-token': self.cookies['XSRF-TOKEN'],
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36',
            'content-type': 'application/json',
            'accept': 'application/json, text/plain, */*',
            'dnt': '1',
            'sec_req_type': 'ajax',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'referer': 'https://www.kroger.com/shopping/list',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9,bn;q=0.8',
        }

        data = {
            "division": division,
            "store_id": store,
            "upcs": upcs
        }
        response = requests.post('https://www.kroger.com/shoppinglist-bff/api/v1/item-locations', headers=headers,
                                 cookies=self.cookies, json=data)
        # pprint.pprint(response.json())
        try:
            aisles = []
            for item in response.json():
                try:
                    aisle = item['aisleNumber'] if 'aisle' in item['aisleDescription'].lower() else item[
                        'aisleDescription']
                    aisles.append([self.product_name(item['itemId']), aisle])
                except (KeyError, IndexError, AttributeError):
                    pass
            return aisles
        except JSONDecodeError:
            print('error')
            return

    def save_store_data(self):
        with open('site_cache/stores.json', 'w') as f:
            f.write(json.dumps(self.stores, indent=2))

        header = ['searched_zip', 'banner', 'divisionNumber',
                  'storeNumber', 'address', 'zip', 'latitude', 'longitude']
        stores_data = self.cached_stores + [[
            store['searched_zip'],
            store['banner'],
            store['divisionNumber'],
            store['storeNumber'],
            store['address'],
            store['zip'],
            store['latitude'],
            store['longitude'],
        ] for store in self.stores]

        with open('site_cache/stores.csv', 'w', encoding='utf-8', newline='') as f:
            csv_writer = csv.writer(f)
            csv_writer.writerow(header)
            for store in stores_data:
                csv_writer.writerow(store)

    def load_store_data(self):
        if not os.path.exists('site_cache/stores.json'):
            print('store_id data not found in site cache')
            quit()

        with open('site_cache/stores.json', 'r') as f:
            self.stores = json.loads(f.read())

    def save_upc_data(self):
        header = ['product', 'upc']
        upcs = self.cached_upcs + self.upcs

        with open('site_cache/upc.csv', 'w', encoding='utf-8', newline='') as f:
            csv_writer = csv.writer(f)
            csv_writer.writerow(header)
            for upc in upcs:
                csv_writer.writerow(upc)

    @staticmethod
    def save_aisle_data(data, filename):
        added_products = []
        clean_data = []
        for product in data:
            if product[0] in added_products:
                pass
            else:
                added_products.append(product[0])
                clean_data.append(product)
        print(f'saving {filename}')
        with open('aisle_data/' + filename, 'w', encoding='utf-8', newline='') as f:
            csv_writer = csv.writer(f)
            for row in clean_data:
                csv_writer.writerow(row)


if __name__ == '__main__':
    print('make sure that you have updated the cookies recently')
    input('press enter to continue scraping...')

    print('choose an option:')
    print('1. search stores')
    print('2. get aisles')
    option = input('option: ')
    kroger = Kroger()

    if option == '1':
        print('searching for stores...')
        for zc in kroger.zip_codes:
            kroger.search_stores(zc)
        kroger.save_store_data()
    elif option == '2':
        kroger.load_store_data()

        print('getting product upcs...')
        for product in kroger.products:
            kroger.find_upc(product)
        kroger.save_upc_data()
        print('*' * 50)

        kroger.get_all_product_upcs()

        # pprint.pprint(kroger.stores)
        for store in kroger.stores:
            try:
                store_banner = store.get('banner')
                if store_banner == '' or store_banner is None:
                    store_banner = 'KROGER'
                filename = store_banner + '-' + store.get('divisionNumber') + '-' + store.get(
                    'storeNumber') + '.csv'
            except TypeError:
                continue
            if os.path.exists(f'aisle_data/{filename}'):
                print(filename, 'already scraped')
            else:
                aisle_data = kroger.get_aisle_numbers(
                    division=store['divisionNumber'],
                    store=store['storeNumber'],
                    upcs=list(kroger.all_product_upcs.keys())
                )
                if aisle_data:
                    kroger.save_aisle_data(data=aisle_data, filename=filename)
    else:
        print('choose a valid option')
