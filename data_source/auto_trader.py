import requests
import json
from data_source import car_fax
import pprint
from data_source.car_schema import car_schema
import copy


def get_listings(zipcode=30307, distance=200, max_mileage=100000, max_price=20000, min_year=2014):
    url = "http://www.autotrader.com/rest/searchresults/base"

    first_record = 0
    full_list = []
    while True:
        querystring = {"zip": str(zipcode),
                       "makeCodeList": "SUB",
                       "modelCodeList": "SUBOUTBK",
                       "startYear": str(min_year),
                       "endYear": "2020",
                       "searchRadius": str(distance),
                       "maxPrice": str(max_price),
                       "maxMileage": str(max_mileage),
                       "numRecords": "100",
                       "firstRecord": str(first_record)}

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'DNT': '1',
            'Host': 'www.autotrader.com',
            'Pragma': 'no-cache',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'

        }

        response = requests.request("GET", url, headers=headers, params=querystring)

        response = json.loads(response.content)
        listings = response['listings']
        owners = response['owners']
        owners = build_dict(owners, "id")

        for listing in listings:
            owner_id = listing['owner']
            listing['owner_details'] = owners.get(owner_id)

        full_list = full_list + listings
        if response['totalResultCount'] < first_record + 100:
            print("Total Results: {}".format(response['totalResultCount']))
            break
        else:
            first_record = first_record + 100
            print(f"moving to record set {first_record}")

    full_list = normalize(full_list)

    return full_list


def build_dict(seq, key):
    return dict((d[key], dict(d, index=index)) for (index, d) in enumerate(seq))


def normalize(listings):
    for listing in listings:
        try:
            listing['listings'] = dict(auto_trader=copy.deepcopy(listing))
            listing['links'] = dict(auto_trader="http://www.autotrader.com" + listing['website']['href'])
            listing['mileage'] = int(listing['specifications']['mileage']['value'].replace(',', ''))
            listing['price'] = listing['pricingDetail']['primary']
            listing['phone'] = listing['owner_details']['phone']['value']
        except KeyError as e:
            print("Key Error on : " + str(e))

        for key in list(listing):
            if key not in car_schema:
                del listing[key]
    return listings


def set_car_fax(car):
    if 'auto_trader' not in car['listings']:
        print("Error parsing car history -- not a auto_trader car")
    elif car['listings']['auto_trader']['productTiles'][0]['link']['href'].__contains__('experian'):
        print(f"Skipping Experian Link {car['vin']}")
    else:
        url = car['listings']['auto_trader']['productTiles'][0]['link']['href']
        accident, damage, owners = car_fax.get_car_fax(url=url)
        car['damage'] = damage
        car['owners'] = owners
    return car


if __name__ == "__main__":
    pprint.pprint(get_listings()[0])
