import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify, url_for, request


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return (
        f"<h2>Welcome to the Hawaii Climate Analysis API!</h2>"
        f"Available Routes:<br/>"
        f"<ul>"
        f"<li>Precipitation <a href=\"/api/v1.0/precipitation\">/api/v1.0/precipitation</a></li>"
        f"<li>Stations <a href=\"/api/v1.0/stations\">/api/v1.0/stations</a></li>"
        f"<li>Temperature Observations <a href=\"/api/v1.0/tobs\">/api/v1.0/tobs</a></li>"
        f"<li>Minimum, average and maximum temperature for a period <a href=\"/api/v1.0/temp/start/end\">/api/v1.0/temp/yyyy-mm-dd/yyyy-mm-dd</a></li>"
        f"</ul>"
        f"<form action=\"/api/v1.0/temp/\" method=\"post\">"
        f"<label for=\"start\">Start date:</label>"
        f"<input type=\"date\" id=\"start\" name=\"start\" value=\"2016-08-23\" min=\"2016-08-23\" max=\"2017-08-23\"><br/>"
        f"<label for=\"end\">End date:</label>"
        f"<input type=\"date\" id=\"end\" name=\"end\" value=\"2017-08-23\" min=\"2016-08-23\" max=\"2017-08-23\"><br/>"
        f"<input type=\"submit\">"
        f"</form>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation data for the last year"""
    # Calculate the date 1 year ago from last date in database
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query for the date and precipitation for the last year
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).all()

    # Dict with date as the key and prcp as the value
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)


@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations."""
    results = session.query(Station.station).all()

    # Unravel results into a 1D array and convert to a list
    stations = list(np.ravel(results))
    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def temp_monthly():
    """Return the temperature observations (tobs) for previous year."""
    # Calculate the date 1 year ago from last date in database
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query the primary station for all tobs from the last year
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all()

    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))

    # Return the results
    return jsonify(temps)


@app.route("/api/v1.0/temp/", methods=['POST'])
@app.route("/api/v1.0/temp/<start>", methods=['POST'])
@app.route("/api/v1.0/temp/<start>/<end>", methods=['POST'])
def stats(start=None, end=None):
    """Return TMIN, TAVG, TMAX."""

    start = request.form['start']
    end   = request.form['end']

    # Select statement
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        # calculate TMIN, TAVG, TMAX for dates greater than start
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        # Unravel results into a 1D array and convert to a list
        temps = list(np.ravel(results))
        return jsonify(temps)

    # calculate TMIN, TAVG, TMAX with start and stop
    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))
    return jsonify(temps)


if __name__ == '__main__':
    app.run()
