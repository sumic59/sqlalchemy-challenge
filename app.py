###########################################
# imports dependencies
###########################################

import datetime as dt
import sys
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

###########################################
# initializes database
###########################################

engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

###########################################
# creates references to Measurement
# and Station tables
###########################################

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)
session.query(func.count(Measurement.date)).all()
####################################
# initializes Flask app
####################################
app = Flask(__name__)

################################
# initializes Flask Routes
################################

@app.route("/")
def homepage():
    """List of all returnable API routes."""
    return(
        f"(Note: Dates range from 2010-01-01 to 2017-08-23). <br><br>"
        f"Available Routes: <br>"

        f"/api/v1.0/precipitation<br/>"
        f"Returns dates and temperature from the last year. <br><br>"

        f"/api/v1.0/stations<br/>"
        f"Returns a json list of stations. <br><br>"

        f"/api/v1.0/tobs<br/>"
        f"Returns list of Temperature Observations(tobs) for previous year. <br><br>"

        f"/api/v1.0/yyyy-mm-dd/<br/>"
        f"Returns an Average, Max, and Min temperatures for a given start date.<br><br>"

        f"/api/v1.0/yyyy-mm-dd/yyyy-mm-dd/<br/>"
        f"Returns an Average, Max, and Min temperatures for a given date range."
    )

@app.route("/api/v1.0/precipitation") # http://127.0.0.1:5000/api/v1.0/precipitation
def precipitation():
    session = Session(engine)
    """Return Dates and Temp from the last year."""
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= "2016-08-24", Measurement.date <= "2017-08-23").\
        all()
    session.close
    # creates JSONified list
    precipitation_list = [results]

    return jsonify(precipitation_list)

@app.route("/api/v1.0/stations") # http://127.0.0.1:5000/api/v1.0/stations
def stations():
    session = Session(engine)
    """Return a list of stations"""
    results = session.query(Station.name, Station.station, Station.elevation).all()
    session.close
    # creates JSONified list of dictionaries
    station_list = []
    for result in results:
        row = {}
        row['name'] = result[0]
        row['station'] = result[1]
        row['elevation'] = result[2]
        station_list.append(row)
    return jsonify(station_list)

@app.route("/api/v1.0/tobs") # http://127.0.0.1:5000/api/v1.0/tobs
def temp_obs():
    session = Session(engine)
    """Return a list of tobs for the previous year"""
    results = session.query(Station.name, Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= "2016-08-24", Measurement.date <= "2017-08-23").\
        all()
    session.close
    # creates JSONified list of dictionaries
    tobs_list = []
    for result in results:
        row = {}
        row["Station"] = result[0]
        row["Date"] = result[1]
        row["Temperature"] = int(result[2])
        tobs_list.append(row)

    return jsonify(tobs_list)

@app.route('/api/v1.0/<date>/') # Sample URL http://127.0.0.1:5000/api/v1.0/2016-08-24/
def given_date(date):
    session = Session(engine)
    """Return the average temp, max temp, and min temp for the date"""
    results = session.query(func.avg(Measurement.tobs), func.max(Measurement.tobs), func.min(Measurement.tobs)).\
        filter(Measurement.date >= date).all()
    session.close
    # creates JSONified list of dictionaries
    data_list = []
    for result in results:
        row = {}
        row['Start Date'] = date
        row['End Date'] = '2017-08-23'
        row['Average Temperature'] = float(result[0])
        row['Highest Temperature'] = float(result[1])
        row['Lowest Temperature'] = float(result[2])
        data_list.append(row)

    return jsonify(data_list)

@app.route('/api/v1.0/<start_date>/<end_date>/') # http://127.0.0.1:5000/api/v1.0/2016-08-24/2017-08-23/
def query_dates(start_date, end_date):
    session = Session(engine)
    """Return the avg, max, min, temp over a specific time period"""
    results = session.query(func.avg(Measurement.tobs), func.max(Measurement.tobs), func.min(Measurement.tobs)).\
        filter(Measurement.date >= start_date, Measurement.date <= end_date).all()
    session.close
    # creates JSONified list of dictionaries
    data_list = []
    for result in results:
        row = {}
        row["Start Date"] = start_date
        row["End Date"] = end_date
        row["Average Temperature"] = float(result[0])
        row["Highest Temperature"] = float(result[1])
        row["Lowest Temperature"] = float(result[2])
        data_list.append(row)
    return jsonify(data_list)


if __name__ == '__main__':
    app.run(debug=True)