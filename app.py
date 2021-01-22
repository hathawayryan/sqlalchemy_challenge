import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from dateutil.relativedelta import relativedelta
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

Base.classes.keys()

# Save reference to the table
Measurements = Base.classes.measurement
Stations = Base.classes.station

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
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    #returns date and precipitation as json

    # Calculate the date one year from the last date in data set.
    recent_date = session.query(Measurements.date).order_by(Measurements.date.desc()).first()
    recent_date = recent_date[0]

    recent_date = dt.datetime.strptime(recent_date, '%Y-%m-%d')
    year_before_recent = recent_date - relativedelta(years=1)

    # Perform a query to retrieve the data and precipitation scores
    data_for_year = session.query(Measurements.date, Measurements.prcp).\
        filter(Measurements.date>=year_before_recent.date()).\
        filter(Measurements.date<=recent_date.date()).order_by(Measurements.date).all()
    
    session.close()

    all_precipitation = []
    for date, prcp in data_for_year:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        all_precipitation.append(precipitation_dict)

    return jsonify(all_precipitation)

@app.route("/api/v1.0/stations")
def stations():   
    #Returns all the stations as JSON

    session = Session(engine)

    #Lists all available stations
    stations = session.query(Measurements.station).\
    group_by(Measurements.station).all()

    session.close()

    all_stations = list(np.ravel(stations))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs(): 
    #Returns tobs data as JSON

    session = Session(engine)

     # Calculate the date one year from the last date in data set.
    recent_date = session.query(Measurements.date).order_by(Measurements.date.desc()).first()
    recent_date = recent_date[0]

    recent_date = dt.datetime.strptime(recent_date, '%Y-%m-%d')
    year_before_recent = recent_date - relativedelta(years=1)

    most_active_station_year = session.query(Measurements.date, Measurements.tobs).\
        filter(Measurements.date>=year_before_recent.date()).\
        filter(Measurements.date<=recent_date.date()).\
        filter(Measurements.station == "USC00519281").order_by(Measurements.date).all()

    session.close()

    all_tobs = []
    for date, tobs in most_active_station_year:
        tobs_dict = {
            "date" : date,
            "tobs" : tobs
        }
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)

@app.route("/api/v1.0/<start_date>")
def start_date(start_date):
    #Returns min temp, max temp, and average temp as JSON after specified date

    session = Session(engine)
    start_date = dt.datetime.strptime(start_date, '%Y-%m-%d')
    min_temp = session.query(func.min(Measurements.tobs)).\
    filter(Measurements.date>=start_date.date()).all()
    min_temp = min_temp[0][0]

    max_temp = session.query(func.max(Measurements.tobs)).\
    filter(Measurements.date>=start_date.date()).all()
    max_temp = max_temp[0][0]

    avg_temp = session.query(func.avg(Measurements.tobs)).\
    filter(Measurements.date>=start_date.date()).all()
    avg_temp = round(avg_temp[0][0], 1)

    session.close()

    all_temp_data = {
        "Min Temp" : min_temp,
        "Max Temp" : max_temp,
        "Average Temp" : avg_temp
    }

    return jsonify(all_temp_data)

@app.route("/api/v1.0/<start_date>/<end_date>")
def end_date(start_date, end_date):
    #Returns min temp, max temp, and average temp as JSON between specified dates

    session = Session(engine)
    start_date = dt.datetime.strptime(start_date, '%Y-%m-%d')
    end_date = dt.datetime.strptime(end_date, '%Y-%m-%d')

    min_temp = session.query(func.min(Measurements.tobs)).\
    filter(Measurements.date>=start_date.date()).\
    filter(Measurements.date<=end_date.date()).all()
    min_temp = min_temp[0][0]

    max_temp = session.query(func.max(Measurements.tobs)).\
    filter(Measurements.date>=start_date.date()).\
    filter(Measurements.date<=end_date.date()).all()
    max_temp = max_temp[0][0]

    avg_temp = session.query(func.avg(Measurements.tobs)).\
    filter(Measurements.date>=start_date.date()).\
    filter(Measurements.date<=end_date.date()).all()
    avg_temp = round(avg_temp[0][0], 1)

    session.close()

    all_temp_data = {
        "Min Temp" : min_temp,
        "Max Temp" : max_temp,
        "Average Temp" : avg_temp
    }

    return jsonify(all_temp_data)


if __name__ == '__main__':
    app.run(debug=True)
