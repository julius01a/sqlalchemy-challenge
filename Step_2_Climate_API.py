from flask import Flask , jsonify
import sqlalchemy
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import datetime as dt 
from sqlalchemy.orm import scoped_session, sessionmaker
#############################################
# Database Setup
#############################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite",echo=False)

Base = automap_base()

Base.prepare(engine, reflect=True)



Measurement = Base.classes.measurement
Station = Base.classes.station


session = scoped_session(sessionmaker(bind=engine))

last_date = (session
                .query(Measurement.date)
                .order_by(Measurement.date.desc())
                .first()[0])
last_date = dt.datetime.strptime(last_date,"%Y-%m-%d")
last_year = last_date - dt.timedelta(days = 365)


############################################
# Flask Setup
############################################

app = Flask(__name__)

############################################
# Flask Setup
############################################

@app.route("/")
def welcome():

    return (
        "Hawaii Precipitation and Weather Data<br/><br/>"
        "Select from the available routes below:<br/><br/>"
        "Precipiation from 2016-08-23 to 2017-08-23.<br/>"
        "/api/v1.0/precipitation<br/><br/>"
        "All available weather stations.<br/>"
        "/api/v1.0/stations<br/><br/>"
        "Temperature Observations (tobs) from 2016-08-23 to 2017-08-23 for the most active station.<br/>"
        "/api/v1.0/tobs<br/><br/>"
        "Type in a single date (i.e., 2015-01-01) to find out min, max and avg temperature since that date.<br/>"
        "/api/v1.0/<start><br/><br/>"
        "Type in a date range (i.e., 2015-01-01/2015-01-10) to see the min, max and avg temperature for that range.<br/>"
        "/api/v1.0/<start>/<end><br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
	
	lastyear_prcp = (session
							.query(Measurement.date,Measurement.prcp)
							.filter(Measurement.date > last_year)
							.order_by(Measurement.date)
							.all())

	precipitation_data = dict(lastyear_prcp)

	return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
	stations = (session
					.query(Station).all())
	stations_list = list()
	for station in stations:
		stations_dict = dict()
		stations_dict['Station'] = station.station
		stations_dict["Station Name"] = station.name
		stations_dict["Latitude"] = station.latitude
		stations_dict["Longitude"] = station.longitude
		stations_dict["Elevation"] = station.elevation
		stations_list.append(stations_dict)

	return jsonify (stations_list)

@app.route("/api/v1.0/tobs")
def tobs():

	temp_tobs_last_year = (session
							.query(Measurement.tobs,Measurement.date,Measurement.station)
							.filter(Measurement.date > last_year)
							.all())

	temp_list = list()
	for data in temp_tobs_last_year:
		temp_dict = dict()
		temp_dict['Station'] = data.station
		temp_dict['Date'] = data.date
		temp_dict['Temp'] = data.tobs
		temp_list.append(temp_dict)

	return jsonify (temp_list)

@app.route("/api/v1.0/<start>")
def start_stats(start=None):

	start_temps = session.query(
		func.min(Measurement.tobs), 
		func.avg(Measurement.tobs),
		func.max(Measurement.tobs)
	).filter(
		Measurement.date >= start
	).all()


	temp_stats = list()
	for tmin, tavg, tmax in start_temps:
		temp_stats_dict = {}
		temp_stats_dict["Min Temp"] = tmin
		temp_stats_dict["Max Temp"] = tavg
		temp_stats_dict["Avg Temp"] = tmax
		temp_stats.append(temp_stats_dict)

	return jsonify (temp_stats)



@app.route("/api/v1.0/<start>/<end>")
def calc_temps(start=None,end=None):
    temps = session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
    ).filter(
    	Measurement.date >= start,
    	Measurement.date <= end
    ).all()

    begin_end_stats = list()
    for tmin, tavg, tmax in temps:
    	begin_end_stats_dict = dict()
    	begin_end_stats_dict["Min Temp"] = tmin
    	begin_end_stats_dict["Avg Temo"] = tavg
    	begin_end_stats_dict["Max Temp"] = tmax
    	begin_end_stats.append(begin_end_stats_dict)

    return jsonify (begin_end_stats)
 



if __name__ == '__main__':
    app.run(debug=True)