import requests

SHEETY_URL = "https://api.sheety.co/459009bf4a167b8e56fc126f5a5a6653/flightDeals/prices"
headers = {
    "Authorization": "Bearer hasankhan"
}


class DataManager:
    def __init__(self):
        self.destination_data = {}

    def get_destination_data(self):
        response = requests.get(url=SHEETY_URL, headers=headers)
        result = response.json()
        self.destination_data = result['prices']
        return self.destination_data

    def update_destination_codes(self):
        for code in self.destination_data:
            code_params = {
                "price": {
                    "iataCode": code['iataCode']
                }
            }
            response = requests.put(url=f"{SHEETY_URL}/{code['id']}", json=code_params)
