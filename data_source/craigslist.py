import requests
from bs4 import BeautifulSoup
import pprint


def get_listings(zipcode=30307, distance=200, max_mileage=100000, max_price=20000, min_year=2014):

    url = "https://atlanta.craigslist.org/search/cta"
    querystring = {"auto_make_model": "subaru outback",
                   "auto_title_status": ["1", "5"],
                   "hints": "mileage",
                   "max_auto_miles": str(max_mileage),
                   "max_price": str(max_price),
                   "max_auto_year": "2020",
                   "min_auto_miles": "1000",
                   "min_auto_year": str(min_year),
                   "postal": str(zipcode),
                   "search_distance": str(distance)}

    response = requests.request("GET", url, params=querystring)

    bs = BeautifulSoup(response.content, 'html.parser')
    list_of_cars = bs.find('ul', class_='rows')
    list_of_link = list_of_cars.find_all('li')

    listings = []

    # print(len(list_of_link))
    for li in list_of_link:
        link = li.find_all('a')[1]['href']

        listing = {"links":  dict(craigslist=link)}
        # print(link)

        response = requests.get(link)
        try:
            bs = BeautifulSoup(response.content, 'html.parser')
            price = bs.find(class_="price").text

            # print("PRICE:" + price)
            listing['price'] = int(price.replace('$', ''))
        except Exception as e:
            print(str(Exception) + str(e))

        # city_state = bs.find(class_="postingtitletext")
        # city_state = city_state.find('small')
        # listing['city_state'] = str(city_state)
        # listing['city_state'] = listing['city_state'][listing['city_state'].find('(')+1:listing['city_state'].find(')')]

        attributes = bs.find_all(class_='attrgroup')
        for attrs in attributes:
            spans = attrs.find_all('span')
            for span in spans:
                text = span.text.split(" ")

                if text[0] == "VIN:":
                    # print("ID#: " + text[1])
                    listing['vin'] = text[1]

                elif text[0] == "odometer:":
                    # print("Miles: " + text[1])
                    listing['mileage'] = int(text[1])

        listings.append(listing)

    return listings


if __name__ == "__main__":
    pprint.pprint(get_listings()[0])


