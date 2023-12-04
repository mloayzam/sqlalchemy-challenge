# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from datetime import datetime, timedelta

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.measurement

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
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs"
    )

#Route Precipitation
@app.route("/api/v1.0/precipitation")
def get_precipitation():
    # Calculate the date one year ago from the current date
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    most_recent_date1 = datetime.strptime(most_recent_date, '%Y-%m-%d')
    one_year_ago = most_recent_date1 - timedelta(days=365)

    # Query precipitation data for the last year
    results = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= one_year_ago).\
    order_by(Measurement.date).all()
    
    # Convert the results to a dictionary with date and precipitation as the value
    precipitation_data = {result.date: result.prcp for result in results}

    return jsonify(precipitation_data)

#Route Stations
@app.route("/api/v1.0/stations")
def get_stations():
    # Query all stations
    stations = session.query(Measurement.station).\
    group_by(Measurement.station).all()
    
    session.close()

    # Convert list of tuples into normal list
    station_data = list(np.ravel(stations))
    return jsonify(station_data)

#Route tobs
@app.route("/api/v1.0/tobs")
def get_tobs():
    # Find the most active station
    most_active_station = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()[0]

    # Calculate the date one year ago from the current date
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    most_recent_date1 = datetime.strptime(most_recent_date, '%Y-%m-%d')
    year_ago = most_recent_date1 - timedelta(days=365)

    # Query tobs data for the most active station for the last year
    tobs_results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station, Measurement.date >= year_ago).all()
    
    session.close()
    
    # Convert the results to a dictionary
    tobs_data = [{"date": result.date, "tobs": result.tobs} for result in tobs_results]

    return jsonify(tobs_data)


if __name__ == "__main__":
    app.run(port = 8080)