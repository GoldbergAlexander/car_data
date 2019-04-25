from data_source import car_gurus, craigslist, auto_trader, cars
import pymongo
import datetime
import pprint


def magic_merge(dict_one, dict_two):
    for key, item in dict_two.items():
        if key not in dict_one:
            dict_one[key] = item
        elif type(item) is dict:
            dict_one[key] = magic_merge(dict_one[key], dict_two[key])

    return dict_one


def add_car_to_db(car_listings, unindexed_list, collection):
    stats = dict(total_cars=0, existing_cars=0, new_cars=0)
    for car_listing in car_listings:
        stats['total_cars'] += 1
        try:
            vin = car_listing['vin']

            if len(vin) < 7:
                unindexed_list.append(car_listing)
                continue

            existing = collection.find_one({'vin': vin})
            if existing is not None:
                existing = magic_merge(existing, car_listing)
                existing['updated'] = datetime.datetime.now()
                collection.replace_one({'vin': vin}, existing)
                stats['existing_cars'] += 1
            else:
                car_listing['added'] = datetime.datetime.now()
                collection.insert_one(car_listing)
                stats['new_cars'] += 1
        except KeyError:
            unindexed_list.append(car_listing)

    return stats


def get_all_cars(collection):
    stats = dict(auto_trader=dict(), car_gurus=dict(), cars=dict(), craigslist=dict())
    MAX_PRICE = 20000
    MAX_MILES = 80000
    DISTANCE = 200

    unindexed_list = list()

    print("Getting Car Listings from Auto Trader")
    cars_from_auto_trader = auto_trader.get_listings(max_price=MAX_PRICE, distance=DISTANCE, max_mileage=MAX_MILES)
    print("Got {} listings".format(len(cars_from_auto_trader)))
    print("Adding to DB")
    stats['auto_trader'] = add_car_to_db(cars_from_auto_trader, unindexed_list, collection)

    print("Getting Car listings from Cars ")
    cars_from_cars = cars.get_listings(max_price=MAX_PRICE, distance=DISTANCE, max_mileage=MAX_MILES)
    print("Got {} listings".format(len(cars_from_cars)))
    print("Adding to DB")
    stats['cars'] = add_car_to_db(cars_from_cars, unindexed_list, collection)

    print("Getting Car listings from Car Gurus")
    cars_from_car_gurus = car_gurus.get_listings(max_price=MAX_PRICE, distance=DISTANCE, max_mileage=MAX_MILES)
    print("Got {} listings".format(len(cars_from_car_gurus)))
    print("Adding to DB")
    stats['car_gurus'] = add_car_to_db(cars_from_car_gurus, unindexed_list, collection)

    print("Getting Car listings from Craigslist")
    cars_from_craigslist = craigslist.get_listings(max_price=MAX_PRICE, distance=DISTANCE, max_mileage=MAX_MILES)
    print("Got {} listings".format(len(cars_from_craigslist)))
    print("Adding to DB")
    stats['craigslist'] = add_car_to_db(cars_from_craigslist, unindexed_list, collection)

    if len(unindexed_list) > 0:
        print(f'{len(unindexed_list)} car found without vins -- attempting to reconcile by price and mileage')
        for car in unindexed_list:
            existing = collection.find_one({'price': car['price'], 'mileage': car['mileage']})
            if existing is not None:
                existing = magic_merge(existing, car)
                existing['updated'] = datetime.datetime.now()
                collection.replace_one({'vin': existing['vin']}, existing)
                print(f'Reconciled with {existing["vin"]}')

    return stats


if __name__ == "__main__":
    client = pymongo.MongoClient("mongodb+srv://python_db_update:U69ERSsTDPlXm3ND@cardata-2e7nv.mongodb.net/test?retryWrites=true")
    db = client.car_data
    collection = db.cars
    pprint.pprint(print(get_all_cars(collection)))
