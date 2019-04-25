from data_source import auto_trader, car_fax
import pymongo


def get_missing_history(collection):


    # Get Missing History
    stats = dict(total_cars=0, auto_trader_cars=0, history_from_auto_trader=0, history_from_car_fax=0)

    cars_missing_history = list(collection.find({'damage': {'$exists': False}}))
    for car in cars_missing_history:
        stats['total_cars'] += 1
        if 'auto_trader' in car['links']:
            stats['auto_trader_cars'] += 1
            car = auto_trader.set_car_fax(car)
            if 'damage' and 'owners' in car:
                collection.replace_one({'vin': car['vin']}, car)
                stats['history_from_auto_trader'] += 1
                continue
        try:

            accident, damage, owners = car_fax.get_car_fax(vin=car['vin'])
            car['damage'] = accident or damage
            car['owners'] = owners
            collection.replace_one({'vin': car['vin']}, car)
            stats['history_from_car_fax'] += 1
        except Exception:
            print("Could not get carfax")

    return stats


if __name__ == "__main__":
    client = pymongo.MongoClient(
        "mongodb+srv://python_db_update:U69ERSsTDPlXm3ND@cardata-2e7nv.mongodb.net/test?retryWrites=true")

    db = client.car_data
    collection = db.cars
    print(get_missing_history(collection))
