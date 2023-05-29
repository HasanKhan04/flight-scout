from twilio.rest import Client
import smtplib
import requests

ACCOUNT_SID = "AC5e4bace9eefaaa16e8e23b3b3f3eab5d"
AUTH_TOKEN = "c7f522d0d68d9ea1414cb9ac1d209c2c"
LINK = "https://www.google.com/travel/flights?q=Flights%20to%20"
SHEETY_EMAIL_URL = "https://api.sheety.co/459009bf4a167b8e56fc126f5a5a6653/flightDeals/users"
headers = {
    "Authorization": "Bearer hasankhan"
}


class NotificationManager:
    def send_notification(self, message):
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        sms = client.messages.create(
            body=message,
            from_='+15856326092',
            to='+14168389352'
        )
        print(sms.status)

    def send_emails(self, message, flight_info, all_emails):
        for email in all_emails:
            my_email = "hasankhanalt@gmail.com"
            password = "dhavwnvdlocelwei"
            with smtplib.SMTP("smtp.gmail.com", 587) as connection:
                connection.starttls()
                connection.login(user=my_email, password=password)
                connection.sendmail(from_addr=my_email, to_addrs=email,
                                    msg=f"Subject:New Low Price Flight! \n\n{message} \n\n"
                                        f"{LINK}{flight_info.to_city}%20from%20{flight_info.from_city}%20on%{flight_info.from_date}%20through{flight_info.to_date}")