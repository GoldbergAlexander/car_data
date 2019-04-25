import pprint
import get_all_cars
import get_missing_history
import get_missing_phone
import pymongo

client = pymongo.MongoClient(
   "mongodb+srv://python_db_update:U69ERSsTDPlXm3ND@cardata-2e7nv.mongodb.net/test?retryWrites=true")

db = client.car_data
collection = db.cars

general_stats = get_all_cars.get_all_cars(collection)
phone_stats = get_missing_phone.get_missing_phone(collection)
history_stats = get_missing_history.get_missing_history(collection)

print("-"*20 + " General " + "-"*20)
pprint.pprint(general_stats)
print()

print("-"*20 + " Phone " + "-"*20)
pprint.pprint(phone_stats)
print()

print("-"*20 + " History " + "-"*20)
pprint.pprint(history_stats)
print()
