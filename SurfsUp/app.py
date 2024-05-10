# Import the dependencies.
import numpy as np
from flask import Flask, jsonify
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine ("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session =  Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
# Home Page
@app.route("/")
def home(): 
    """List all available api routes"""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )

#################################################
# Precipitation Page
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Query 12 Months of Precipitation data - Return as JSON"""

    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    # Calculate the date one year from the last date in data set.
    init_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    past_12M_prcp = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= init_date).all()

    #close
    session.close()

    # jsonify
    prcp = {date: prcp for date, prcp in past_12M_prcp}
    return jsonify(prcp)
    

#################################################
# Station Page
@app.route("/api/v1.0/stations")
def stations():
    """Query a list of stations - Return as JSON"""

    total_stations= session.query(Measurement.station,func.count(Measurement.station)).\
        order_by(func.count(Measurement.station).desc()).group_by(Measurement.station).all()
   
    #close
    session.close()

    #jsonify
    results = list(np.ravel(total_stations))
    return jsonify(stations = results)

#################################################
# Tobs Page
@app.route("/api/v1.0/tobs")
def tobs():
   """Query the most active station - Return tobs as JSON"""
   init_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
   past_12M_tobs = session.query(Measurement.tobs).filter(Measurement.station=='USC00519281').filter(Measurement.date>= init_date).all()
   
   #jsonify
   tobs = list(np.ravel(past_12M_tobs))
   return jsonify(stations = tobs)

################################################
# Start Page
   
@app.route("/api/v1.0/<start>")
def start(start=None):
    """Query a list of the min, max, and the avg temp for a start date"""
    
    sel=[func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]
    # Tip: Enter a date between 2016-08-23 and 2017-08-23 to get the outcome
    start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    start_data = session.query(*sel).filter(Measurement.date >= start_date).all()
    
    # Close
    session.close()
    
    #jsonify
    start_date_results = list(np.ravel(start_data))
    return jsonify(start_date_results)

#################################################
# Start and End Page
@app.route("/api/v1.0/<start>/<end>")
def start_end(start=None, end=None):
    """Return a list of the min, max and avg temp tobs for start and end dates"""
    
    sel=[func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]
    # Tip: Enter a date between 2016-08-23 and 2017-08-23 to get the outcome
    start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    end_date = dt.datetime.strptime(end, "%Y-%m-%d")
    end_date > start_date 
    start_end_data = session.query(*sel).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    
    # Close
    session.close()
    
    #jsonify
    start_end_results = list(np.ravel(start_end_data))
    return jsonify(start_end_results)

if __name__ == '__main__':
    app.run(debug=True)  

