import sqlalchemy

from flask import Flask
from sqlalchemy import Table, ForeignKey, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

# TODO to git-Bitbucket this project

engine = sqlalchemy.create_engine('postgres://postgres@/postgres')
conn = engine.connect()
conn.execute('commit')


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    employees = relationship('Employee', secondary='department_employee')


class Geolocation(Base):
    __tablename__ = 'geolocations'
    id = Column(Integer, primary_key=True)


class UserGeolocation(Base):
    __tablename__ = 'users_geolocations'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    geolocation_id = Column(Integer, ForeignKey('geolocations.id'), primary_key=True)


session = sessionmaker()
session.configure(bind=engine)
Base.metadata.create_all(engine)

conn.close()


    # app = Flask(__name__)
    #
    # @app.route('/')
    # def hello_world():
    #     return 'Hello World!'
    #
    # if __name__ == '__main__':
    #     app.run()
