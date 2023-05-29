import requests
from flight_data import FlightData

API_KEY = "x_4ZswXjwQ8gKUOKTOlXDpwEmZCENxU1"
TEQUILA_ENDPOINT = "https://api.tequila.kiwi.com"
headers = {
    "apikey": API_KEY
}


class FlightSearch:
    def get_destination_code(self, city_name):
        print("get destination codes triggered")
        flight_config = {
            "term": city_name,
            "location_types": "city"
        }
        response = requests.get(url=f"{TEQUILA_ENDPOINT}/locations/query", params=flight_config, headers=headers)
        result = response.json()
        iata_code = result['locations'][0]['code']
        return iata_code

    def search_flights(self, from_code, to_code, from_time, to_time, stop_overs=0, via_city=""):
        print(f"Check flights triggered for {to_code}")
        search_config = {
            "fly_from": from_code,
            "fly_to": to_code,
            "date_from": from_time,
            "date_to": to_time,
            "nights_in_dst_from": 7,
            "nights_in_dst_to": 28,
            "flight_type": "round",
            "one_for_city": 1,
            "curr": "CAD",
            "max_stopovers": 0
        }

        response = requests.get(url=f"{TEQUILA_ENDPOINT}/v2/search", params=search_config, headers=headers)
        try:
            result = response.json()['data'][0]
        except IndexError:
            search_config['max_stopovers'] = 1
            response = requests.get(url=f"{TEQUILA_ENDPOINT}/v2/search", params=search_config, headers=headers)
            try:
                data = response.json()['data'][0]
            except IndexError:
                return None
            else:
                flight_data = FlightData(
                    price=data['price'],
                    from_city=data['route'][0]['cityFrom'],
                    from_airport=data['route'][0]['flyFrom'],
                    to_city=data['route'][0]['cityTo'],
                    to_airport=data['route'][0]['flyTo'],
                    from_date=data['route'][0]['local_departure'].split("T")[0],
                    to_date=data['route'][1]['local_departure'].split("T")[0],
                    stop_overs=1,
                    via_city=data['route'][0]['cityTo']
                )
                print(f"{flight_data.to_city}: ${flight_data.price}")
                return flight_data
        else:
            flight_data = FlightData(
                price=result['price'],
                from_city=result['route'][0]['cityFrom'],
                from_airport=result['route'][0]['flyFrom'],
                to_city=result['route'][0]['cityTo'],
                to_airport=result['route'][0]['flyTo'],
                from_date=result['route'][0]['local_departure'].split("T")[0],
                to_date=result['route'][1]['local_departure'].split("T")[0]
            )
            print(f"{flight_data.to_city}: ${flight_data.price}")
            return flight_data
