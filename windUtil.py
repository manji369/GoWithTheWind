import requests
import json
import threading
import timeit
from decimal import Decimal
import main as temp

from geopy.distance import vincenty
	
WHEATHER_API_KEY = "bb1ebecae1f1624e5b0e885e8198730e"

# Threading classes
class getWindDataThread(threading.Thread):
	def __init__(self, lat_long_arr, dist_interval, threadID, name):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.lat_long_arr = lat_long_arr
		self.dist_interval = dist_interval

	def run(self):
		print "Starting " + self.name
		self.windData = getWindData(self.lat_long_arr, self.threadID, self.dist_interval)
		
	def get(self):
		return self.windData

# Returns the wind data by making calls to openweathermap API (https://openweathermap.org/api)
def getWindData(lat_long_arr, routeNum, dist_interval):
	windData = []
	
	if len(lat_long_arr) <= 1:
		return windData
	
	j = 0
	while j < len(lat_long_arr)-1:
		prev_lat_long = lat_long_arr[j]
		curr_lat_long = lat_long_arr[j+1]
		mapDist = vincenty(prev_lat_long, curr_lat_long).miles
		
		# If the intermediate poly points are within the dist_interval that is specified in CONSTANTS in main, skip that point
		while mapDist < dist_interval and j < len(lat_long_arr):
			curr_lat_long = lat_long_arr[j]
			mapDist = vincenty(prev_lat_long, curr_lat_long).miles
			j += 1
		
		windForceObj = windForceClass(None)
		windData.append(getWindAt(curr_lat_long, windForceObj))
		windForceObj.dist = mapDist
		j += 1
	return windData

# Storing the json in objects
def getWindAt(curr_lat_long, windForceObj):
	api_call_url = "http://api.openweathermap.org/data/2.5/weather?lat=" + str(curr_lat_long[0]) + "&lon=" + str(curr_lat_long[1]) + "&appid=" + WHEATHER_API_KEY
	windAPI_responseJSON = json.loads(requests.post(api_call_url, None).text, parse_float = Decimal)
	windForceObj.populateObj(windAPI_responseJSON)
	return windForceObj


class windForceClass:
	
	def __init__(self, input_json):
		self.json_data = input_json
		self.coord = None
		self.wind = None
		self.dist = 0.
		
	def populateObj(self, input_json):
		self.json_data = input_json
		self.coord = {"lat":Decimal(self.json_data["coord"]["lat"]), "lon":Decimal(self.json_data["coord"]["lon"])}
		self.wind = {"speed":self.json_data["wind"]["speed"],"deg":self.json_data["wind"]["deg"]}
		self.dist = 0.
		
		