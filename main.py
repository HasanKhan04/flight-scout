from flask import Flask, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from forms import RegisterForm, LoginForm, ContactForm
from sqlalchemy.ext.declarative import declarative_base

from data_manager import DataManager
from flight_search import FlightSearch
from notification_manager import NotificationManager
import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
ckeditor = CKEditor(app)
Bootstrap(app)
login_manager = LoginManager()

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flight.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager.init_app(app)
Base = declarative_base()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(250), nullable=False)
    last_name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False)
    password = db.Column(db.String(250), nullable=False)
    comments = relationship('Comment', back_populates="comment_author")


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comment_author = relationship("User", back_populates="comments")


with app.app_context():
    db.create_all()


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))
        else:
            secure_pass = generate_password_hash(form.password.data, 'pbkdf2:sha256', 8)
            new_user = User()
            new_user.email = form.email.data
            new_user.password = secure_pass
            new_user.first_name = form.first_name.data
            new_user.last_name = form.last_name.data
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('home'))
    return render_template("register.html", form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, form.password.data):
            flash("Password incorrect, please try again.")
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('home'))
    return render_template("login.html", form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to log in or register to contact us.")
            return redirect(url_for('login'))
        email = form.email.data
        person = User.query.filter_by(email=form.email.data).first()
        if not person:
            flash("That email is not registered, try again.")
            return redirect(url_for('contact'))
        new_comment = Comment()
        new_comment.text = form.message.data
        new_comment.comment_author = current_user
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for('contact'))
    return render_template("contact.html", form=form)


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


if __name__ == "__main__":
    app.run(debug=True)
