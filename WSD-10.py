from random import randint
import json

import sqlalchemy
from sqlalchemy import Table, Column, String, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import requests

from flask import Flask
import flask

Base = declarative_base()

engine = sqlalchemy.create_engine('postgres://postgres@/postgres')

Session = sessionmaker()
Session.configure(bind=engine)
session = Session()

association_table = Table('association', Base.metadata,
                          Column('user_id', Integer, ForeignKey('user.id', ondelete='CASCADE')),
                          Column('geolocation_id', Integer, ForeignKey('geolocation.id', ondelete='CASCADE'))
                          )


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    geolocation = relationship('Geolocation', secondary=association_table, backref='geolocations',
                               cascade='all,delete-orphan', single_parent=True)


class Geolocation(Base):
    __tablename__ = 'geolocation'
    id = Column(Integer, primary_key=True)
    city = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    user = relationship('User', secondary=association_table, backref='users')


Base.metadata.create_all(engine)

app = Flask(__name__)


@app.route('/get_users_location')
def get_user_locations():
    user_names = ['Vitaly Zdanevich', 'Vladimir Posner', 'Yuri Burlan', 'Michael Laitman', 'Pavel Durov', 'Kate',
                  'John', 'Veras', 'Mike', 'Alex', 'Vlad', 'Yulia', 'Nastia']
    cities = ['Minsk', 'Moscow', 'New York', 'Bnei Brak', 'Saint Petersburg', 'Brest', 'Kiev', 'Sydney', 'Washington',
              'Las Vegas', 'Berlin', 'Vladivostok', 'Vienna']

    dict_for_json = {}

    for i in range(5):
        user_name = user_names[randint(0, len(user_names)) - 1]
        city_name = cities[randint(0, len(cities)) - 1]

        req = requests.get('http://maps.googleapis.com/maps/api/geocode/json?address=' + city_name)
        jsn = json.loads(req.text)
        lat = jsn['results'][0]['geometry']['location']['lat']
        lng = jsn['results'][0]['geometry']['location']['lng']

        new_user = User(name=user_name)
        new_city = Geolocation(city=city_name, latitude=lat, longitude=lng)

        session.query(User).filter(User.name == user_name).delete()
        session.query(Geolocation).filter(Geolocation.city == city_name).delete()

        new_user.geolocation.append(new_city)
        session.add(new_user, new_city)

        # because key is random user - json at page can have less that 5 results (some user can chosen twice)
        dict_for_json[user_name] = [city_name, lat, lng]

        session.commit()

    session.close()

    return flask.Response(json.dumps(dict_for_json, sort_keys=True, indent=4), status=200, mimetype='application/json')


if __name__ == '__main__':
    app.run()
