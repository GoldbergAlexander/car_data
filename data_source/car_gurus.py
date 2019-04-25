import requests
import json
from data_source.car_schema import car_schema
from bs4 import BeautifulSoup
import pprint
import copy


def get_listings(zipcode=30307, distance=200, max_mileage=100000, max_price=20000, min_year=2014):

    zipcode = str(zipcode)
    distance = str(distance)
    url = "https://www.cargurus.com/Cars/inventorylisting/ajaxFetchSubsetInventoryListing.action"

    payload = "------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"zip\"\r\n\r\n"+zipcode+"\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"distance\"\r\n\r\n"+distance+"\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"selectedEntity\"\r\n\r\nd380\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"page\"\r\n\r\n1\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--"

    headers = {
        'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
        'cache-control': "no-cache",
    }

    response = requests.request("POST", url, data=payload, headers=headers)

    response = json.loads(response.content)

    listings = response['listings']

    listings = filter_listings(listings, max_mileage, max_price, min_year)
    listings = normalize(listings)

    return listings


def get_phone(listing_id):
    print(f'Getting phone for listing {listing_id}')
    url = "https://www.cargurus.com/Cars/inventorylisting/viewListingDetailAjax.action"
    querystring = {"inventoryListing": listing_id}

    response = requests.request("GET", url, params=querystring)

    details = BeautifulSoup(response.content, 'html.parser')
    phone = details.find(id='dealerPhoneNumber').text
    phone = ''.join(filter(lambda x: x.isdigit(), phone))
    print(f'Got phone number {phone}')
    return phone


def filter_listings(listings, max_mileage=100000, max_price=20000, min_year=2014):
    try:
        listings = [listing for listing in listings if int(listing['carYear']) >= min_year]
        listings = [listing for listing in listings if int(listing['price']) <= max_price]
        listings = [listing for listing in listings if int(listing['price']) > 0]
        listings = [listing for listing in listings if int(listing['mileage']) <= max_mileage]
        listings = [listing for listing in listings if int(listing['mileage']) > 0]
    except KeyError:
        print("KeyError")
    return listings


def normalize(listings):
    for listing in listings:
        try:
            listing['listings'] = dict(car_gurus=copy.deepcopy(listing))
            listing['links'] = dict(car_gurus=f'https://www.cargurus.com/Cars/inventorylisting/viewListingDetailAjax.action?inventoryListing={listing["id"]}')
            listing['year'] = int(listing['carYear'])
            listing['mileage'] = int(listing['mileage'])
            listing['vin'] = listing['vehicleIdentifier']
            listing['damage'] = bool(listing['hasAccidents'] or listing['frameDamaged'])
            listing['owners'] = listing['ownerCount']
        except KeyError as a:
            print(str(KeyError) + str(a))

        for key in list(listing):
            if key not in car_schema:
                del listing[key]

    return listings


def get_phone_for_car(listing):
        listing['phone'] = get_phone(listing['listings']['car_gurus']['id'])
        return listing


if __name__ == "__main__":
    pprint.pprint(get_listings()[0])

