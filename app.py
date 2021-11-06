import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import pandas as pd
import datetime as dt


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

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
        f"/api/v1.0/<start><br/>"
        f"-date format (YYYY-MM-DD)<br/> "
        f"/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query all data  

    year_prcp = session.query(Measurement.date, Measurement.prcp).all()

    #Query data within a year
    #latest_date =  dt.date(2017, 8, 23)
    #year_ago = latest_date - dt.timedelta(days=365)
    #year_prcp = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >=year_ago).all()

    session.close()

    # Convert the query results to a dictionary using `date` as the key and `prcp`
    daily_a_yr_prcp= {date: prcp for date, prcp in year_prcp}
    
    return jsonify(daily_a_yr_prcp)

@app.route("/api/v1.0/stations")
def stations():
    # Return a JSON list of stations from the dataset.
    session = Session(engine)
    all_stations = session.query(Station.station).all()

    session.close()
    
    return jsonify(all_stations)
    
    # Query the dates and temperature observations of the most active station for the last year of data.
@app.route("/api/v1.0/tobs")
def measurement():
    
    session = Session(engine)

    latest_date =  dt.date(2017, 8, 23)
    last_year= latest_date - dt.timedelta(days=365)

    active_station_tobs = session.query(Measurement.tobs).filter(Measurement.date >= last_year, Measurement.station =='USC00519281').all()

    session.close()

    return jsonify(active_station_tobs)

    # When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.

@app.route("/api/v1.0/<start>")
def start(start = None):

    
    session = Session(engine)

    latest_date =  dt.date(2017, 8, 23)
    temp_data = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.round(func.avg(Measurement.tobs),2)).\
                   filter(Measurement.date.between(start, latest_date)).all()

   
    session.close()
    temp = list(np.ravel(temp_data))
    return jsonify(temp)


    # When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.

@app.route("/api/v1.0/<start>/<end>")
def startend(start = None, end = None):
    
    session = Session(engine)

    temp_data2 = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.round(func.avg(Measurement.tobs),2)).\
                   filter(Measurement.date.between(start, end)).all()

        
    session.close()
    temp2 = list(np.ravel(temp_data2))
    return jsonify(temp2)


if __name__ == '__main__':
    app.run(debug=True)
