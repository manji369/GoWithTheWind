import requests
import json
import threading
import time
from decimal import Decimal
import main as temp

from geopy.distance import vincenty

GOOGLE_API_KEY = "AIzaSyD8oG2O067lnxI0ga9TBsJH_lS5F2ARTvY"

# Threading classes
class getElevDataThread(threading.Thread):
	def __init__(self, lat_long_arr, dist_interval, threadID, name):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.lat_long_arr = lat_long_arr
		self.dist_interval = dist_interval

	def run(self):
		print "Starting " + self.name
		self.elevData = getElevData(self.lat_long_arr, self.dist_interval)
		
	def get(self):
		return self.elevData


# Returns the elevation data by making calls to Google Elevation API
def getElevData(lat_long_arr, dist_interval):
	elevData = []
	
	if len(lat_long_arr) <= 1:
		return elevData
	
	i = 0
	selected_lat_long_arr = []
	selected_lat_long_arr.append(lat_long_arr[0])
	
	while i < len(lat_long_arr)-1:
		prev_lat_long = lat_long_arr[i]
		curr_lat_long = lat_long_arr[i+1]
		
		mapDist = vincenty(prev_lat_long, curr_lat_long).miles
		
		# If the intermediate poly points are within the dist_interval that is specified in CONSTANTS in main, skip that point
		while mapDist < dist_interval and i < len(lat_long_arr):
			curr_lat_long = lat_long_arr[i]
			mapDist = vincenty(prev_lat_long, curr_lat_long).miles
			i += 1
		
		selected_lat_long_arr.append(curr_lat_long)
		i += 1

	lat_long_string = []
	
	# Making a string of all coordinates to pass to elevation API 
	for i in xrange(len(selected_lat_long_arr)):
		lat_long_string.append(str(selected_lat_long_arr[i][0]) + "," + str(selected_lat_long_arr[i][1]) + "|")
	lat_long_string = ''.join(lat_long_string)
	lat_long_string = lat_long_string[:-1]
	
	# Making API call
	api_call_url = "https://maps.googleapis.com/maps/api/elevation/json?locations=" + lat_long_string + "&key=" + GOOGLE_API_KEY
	elevAPI_responseJSON = json.loads(requests.post(api_call_url, None).text)
	
	# Storing the json in objects
	obj_arr = []
	for poly_id in xrange(len(selected_lat_long_arr)):
		elevForceObj = elevForceClass(None)
		elevForceObj.populateObj(elevAPI_responseJSON, poly_id)
		if poly_id==0:
			elevForceObj.dist = 0.
		else:
			elevForceObj.dist = vincenty(selected_lat_long_arr[poly_id-1], selected_lat_long_arr[poly_id]).miles
		obj_arr.append(elevForceObj)
	return obj_arr


class elevForceClass:
	
	def __init__(self, input_json):
		self.json_data = input_json
		self.coord = None
		self.elev = None
		self.dist = 0.
		
	def populateObj(self, input_json, poly_id):
		self.json_data = input_json
		self.coord = {"lat":self.json_data["results"][poly_id]["location"]["lat"], "lon":self.json_data["results"][poly_id]["location"]["lng"]}
		self.elev = self.json_data["results"][poly_id]["elevation"]
		self.dist = 0.
