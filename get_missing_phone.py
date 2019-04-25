from data_source import car_gurus
import pymongo


def get_missing_phone(collection):



    # Get Missing Phone
    stats = dict(total_cars=0, car_gurus_cars=0, got_phone=0)
    cars_missing_phone = list(collection.find({'phone': {'$exists': False}}))
    for car in cars_missing_phone:
        stats['total_cars'] += 1
        if 'car_gurus' in car['links']:
            stats['car_gurus_cars'] += 1
            car = car_gurus.get_phone_for_car(car)
            if 'phone' in car:
                stats['got_phone'] += 1
                collection.replace_one({'vin': car['vin']}, car)

    return stats


if __name__ == "__main__":
    client = pymongo.MongoClient(
        "mongodb+srv://python_db_update:U69ERSsTDPlXm3ND@cardata-2e7nv.mongodb.net/test?retryWrites=true")

    db = client.car_data
    collection = db.cars
    print(get_missing_phone(collection))
