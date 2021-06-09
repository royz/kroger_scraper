# encoding: utf-8

import re
import os
import csv
import glob
import requests


def get_user_details():
    if os.path.exists('user.txt'):
        with open('user.txt') as file:
            user = file.read().split('\n')
        if len(user) != 2:
            print('enter user details in the correct format inside user.txt')
            print('first line should contain the username and second line the password')
            quit()
        else:
            return user
    else:
        print('user.txt not found')
        quit()


def login(username, password):
    """logs in to the site with given user details and returns the cookies"""

    print('logging in...')
    url = 'https://www.speedshopperapp.com/app/admin/login'
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,bn;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'DNT': '1',
        'Host': 'www.speedshopperapp.com',
        'Origin': 'https://www.speedshopperapp.com',
        'Referer': 'https://www.speedshopperapp.com/app/admin/login',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36'
    }

    payload = {
        'username': username,
        'password': password
    }
    session = requests.session()
    session.post(url, headers=headers, data=payload)
    print('logged in')
    return session.cookies


def search_stores(cookies, name='', address=''):
    """searches the website for all available stores and saves their details for quick access"""
    url = 'https://www.speedshopperapp.com/app/admin/stores/getstores'

    data = {
        'draw': '2',
        'columns[0][data]': '0',
        'columns[0][name]': '',
        'columns[0][searchable]': 'true',
        'columns[0][orderable]': 'true',
        'columns[0][search][value]': '',
        'columns[0][search][regex]': 'false',
        'columns[1][data]': '1',
        'columns[1][name]': '',
        'columns[1][searchable]': 'true',
        'columns[1][orderable]': 'true',
        'columns[1][search][value]': '',
        'columns[1][search][regex]': 'false',
        'columns[2][data]': '2',
        'columns[2][name]': '',
        'columns[2][searchable]': 'true',
        'columns[2][orderable]': 'true',
        'columns[2][search][value]': '',
        'columns[2][search][regex]': 'false',
        'columns[3][data]': '3',
        'columns[3][name]': '',
        'columns[3][searchable]': 'true',
        'columns[3][orderable]': 'true',
        'columns[3][search][value]': '',
        'columns[3][search][regex]': 'false',
        'columns[4][data]': '4',
        'columns[4][name]': '',
        'columns[4][searchable]': 'true',
        'columns[4][orderable]': 'true',
        'columns[4][search][value]': '',
        'columns[4][search][regex]': 'false',
        'columns[5][data]': '5',
        'columns[5][name]': '',
        'columns[5][searchable]': 'true',
        'columns[5][orderable]': 'true',
        'columns[5][search][value]': '',
        'columns[5][search][regex]': 'false',
        'columns[6][data]': '6',
        'columns[6][name]': '',
        'columns[6][searchable]': 'true',
        'columns[6][orderable]': 'true',
        'columns[6][search][value]': '',
        'columns[6][search][regex]': 'false',
        'columns[7][data]': '7',
        'columns[7][name]': '',
        'columns[7][searchable]': 'true',
        'columns[7][orderable]': 'true',
        'columns[7][search][value]': '',
        'columns[7][search][regex]': 'false',
        'columns[8][data]': '8',
        'columns[8][name]': '',
        'columns[8][searchable]': 'true',
        'columns[8][orderable]': 'false',
        'columns[8][search][value]': '',
        'columns[8][search][regex]': 'false',
        'order[0][column]': '0',
        'order[0][dir]': 'asc',
        'start': '0',
        'length': '50000',
        'search[value]': '',
        'search[regex]': 'false',
        'name': name,
        'address': address
    }

    headers = {
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Origin': 'https://www.speedshopperapp.com',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36',
        'DNT': '1',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Referer': 'https://www.speedshopperapp.com/app/admin/stores',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,bn;q=0.8',
    }

    res = requests.post(url, headers=headers, cookies=cookies, data=data)
    try:
        data = res.json()['data'][0]
        return re.search(r'[0-9]+', data[4]).group()
    except IndexError:
        return None


def get_files():
    files = glob.glob('aisle_data/*.csv')
    if len(files) == 0:
        print('no csv files found under input_files folder')
        quit()
    count = len(files)
    print(f'{count} {"file" if count == 1 else "files"} found')
    return files


def get_import_id():
    if os.path.exists('import-id.txt'):
        with open('import-id.txt') as f:
            try:
                return int(f.read())
            except:
                pass
    return 2266


def get_form_body(file_path, filename, store_id):
    with open(file_path, encoding='utf-8') as f:
        data = f.read().strip()

    if not os.path.exists('request-body.txt'):
        print('request-body.txt not found')
        quit()

    with open('request-body.txt') as f:
        body = f.read().strip() % (user_id, filename, data, store_id)
    return body.encode('utf-8')


def import_file(cookies, file_path, filename, store_id):
    """imports a csv file in the website"""
    headers = {
        'Host': 'www.speedshopperapp.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'multipart/form-data; boundary=---------------------------1267546269709',
        'Origin': 'https://www.speedshopperapp.com',
        'Connection': 'keep-alive',
        'Referer': f'https://www.speedshopperapp.com/app/admin/stores/import/{store_id}',
        'Upgrade-Insecure-Requests': '1',
    }

    response = requests.post('https://www.speedshopperapp.com/app/admin/stores/importFile',
                             data=get_form_body(file_path, filename, store_id), headers=headers, cookies=cookies)

    if 'Imported items successfully' in response.text:
        return True
    return False


class Address:
    def __init__(self):
        self.stores = {}
        self.get_store_data()

    def get_address(self, store_id):
        return self.stores.get(store_id)

    def get_store_data(self):
        if not os.path.exists('site_cache/stores.csv'):
            return []

        with open('site_cache/stores.csv') as f:
            reader = csv.reader(f)
            try:
                next(reader)
            except StopIteration:
                return []
            stores = list(reader)

        for store in stores:
            self.stores[store[2] + store[3]] = store[4]


if __name__ == '__main__':
    user_id = get_import_id()
    csv_files = get_files()
    username, password = get_user_details()
    cookies = login(username=username, password=password)
    address = Address()
    print('=' * 75)

    for file in csv_files:
        filename = file.split('\\')[-1]
        print(f'filename: {filename}')
        divisionNumber = filename[:-4].split('-')[-2]
        storeNumber = filename[:-4].split('-')[-1]
        store_id = divisionNumber + storeNumber
        print(f'store_id id: {store_id}')
        street_address = address.get_address(store_id=store_id)
        print(f'street address: {street_address}')
        site_id = search_stores(cookies, address=street_address)
        if not site_id:
            print('store_id not found on speedshopperapp')
            print('=' * 75)
            continue
        print(f'import url: https://www.speedshopperapp.com/app/admin/stores/import/{site_id}')
        success = import_file(cookies, file, filename, site_id)
        if success:
            print('imported successfully')
        else:
            print('failed to import')
        print('=' * 75)
