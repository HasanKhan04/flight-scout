from data_manager import DataManager
from flight_search import FlightSearch
from notification_manager import NotificationManager
import datetime
from main import User, app

FROM = "YYZ"
data_manager = DataManager()
flight_search = FlightSearch()
notification_manager = NotificationManager()
sheet_data = data_manager.get_destination_data()
with app.app_context():
    all_emails = [row.email for row in User.query.all()]


for i in range(len(sheet_data)):
    if sheet_data[i]['iataCode'] == "":
        for j in range(len(sheet_data)):
            sheet_data[j]['iataCode'] = flight_search.get_destination_code(sheet_data[j]["city"])
            data_manager.destination_data = sheet_data
        data_manager.update_destination_codes()

tomorrow = datetime.datetime.now() + datetime.timedelta(1)
six_months = tomorrow + datetime.timedelta(180)
tomorrow = tomorrow.strftime("%d/%m/%Y")
six_months = six_months.strftime("%d/%m/%Y")

for city in sheet_data:
    flight_info = flight_search.search_flights(FROM, city['iataCode'], tomorrow, six_months)
    if flight_info is None:
        continue
    if city['lowestPrice'] > flight_info.price:
        message = f"Low price alert! Only ${flight_info.price} to fly from {flight_info.from_city}-" \
                  f"{flight_info.from_airport} to {flight_info.to_city}-{flight_info.to_airport}, from {flight_info.from_date} to {flight_info.to_date}."
        if flight_info.stop_overs > 1:
            message += f"\nFlight has {flight_info.stop_overs} stopover, via {flight_info.via_city}"
        notification_manager.send_notification(message)
        notification_manager.send_emails(message, flight_info, all_emails)