import requests
from bs4 import BeautifulSoup
import copy
from data_source.car_schema import car_schema
import json
import pprint


def get_listings(zipcode=30307, distance=200, max_mileage=100000, max_price=20000, min_year=2014):
    full_list = []
    page = 1
    while True:
        MAX_PAGE_SIZE = 100
        URL = "https://www.cars.com"
        PATH = "/for-sale/searchresults.action/"
        PARAMS = {'mdId': '21697',
                  'mkId': '20041',
                  'page': str(page),
                  'perPage': str(MAX_PAGE_SIZE),
                  'prMx': str(max_price),
                  'rd': str(distance),
                  'showMore': 'false',
                  'sort': 'year-newest',
                  'stkTypId': '28881',
                  'zc': str(zipcode)}

        response = requests.get(URL+PATH, params=PARAMS)
        bs = BeautifulSoup(response.content, 'html.parser')

        script_tag = bs.head.find_all('script')[1]

        json_text = script_tag.text.strip().replace('window.CARS = window.CARS || {};\n    CARS.digitalData = ','')
        json_text = json_text.replace(';', '\n')
        json_data = json.loads(json_text)
        full_list = full_list + json_data['page']['vehicle']
        if len(json_data['page']['vehicle']) > 0:
            print("moving to page: {}".format(page+1))
            page = page + 1
        else:
            break

    full_list = filter_listings(full_list, max_mileage, min_year)
    full_list = normalize(full_list)

    return full_list


def filter_listings(listings, max_mileage=100000, min_year=2014):
    listings = [listing for listing in listings if int(listing['year']) >= min_year]
    listings = [listing for listing in listings if int(listing['mileage']) <= max_mileage]
    listings = [listing for listing in listings if int(listing['mileage']) > 0]
    return listings


def normalize(listings):
    for listing in listings:
        listing['listings'] = dict(cars=copy.deepcopy(listing))
        listing['links'] = dict(cars=f'https://www.cars.com/vehicledetail/detail/{listing["listingId"]}/overview/')
        listing['phone'] = listing['seller']['phoneNumber']
        listing['mileage'] = int(listing['mileage'])

        for key in list(listing):
            if key not in car_schema:
                del listing[key]
    return listings


if __name__ == "__main__":
    pprint.pprint(get_listings()[0])
