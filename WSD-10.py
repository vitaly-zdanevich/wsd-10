import sqlalchemy

from flask import Flask
from sqlalchemy import Column, String, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import requests
import json

Base = declarative_base()
engine = sqlalchemy.create_engine('postgres://postgres@/postgres')


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    geolocation = relationship('Geolocation', secondary='users_geolocations')


class Geolocation(Base):
    __tablename__ = 'geolocations'
    id = Column(Integer, primary_key=True)
    city = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    user = relationship('User', secondary='users_geolocations')


class UserGeolocation(Base):
    __tablename__ = 'users_geolocations'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    geolocation_id = Column(Integer, ForeignKey('geolocations.id'), primary_key=True)


Session = sessionmaker()
Session.configure(bind=engine)
session = Session()
Base.metadata.create_all(engine)

users = {
    'Vitaly Zdanevich': 'Minsk',
    'Vladimir Posner': 'Moscow',
    'Yuri Burlan': 'New York',
    'Michael Laitman': 'Bnei Brak',
    'Pavel Durov': 'Saint Petersburg'
}

for user in users:
    city = users[user]
    req = requests.get('http://maps.googleapis.com/maps/api/geocode/json?address='+city)
    jsn = json.loads(req.text)
    lat = jsn['results'][0]['geometry']['location']['lat']
    lng = jsn['results'][0]['geometry']['location']['lng']

    new_user = User(name=user)
    city = Geolocation(city=users[user], latitude=lat, longitude=lng)

    new_user.geolocation.append(city)
    session.add(new_user, city)

session.commit()
session.close()

# app = Flask(__name__)
#
# @app.route('/')
# def hello_world():
#     return 'Hello World!'
#
# if __name__ == '__main__':
#     app.run()
