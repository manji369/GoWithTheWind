import threading
import polyline
import json
import requests
import windUtil
import elevUtil
import geopy
import math

from costFunctionUtil import elevCost, windCost
from geopy.distance import vincenty

# CONSTANTS
WIND_DIST_INTERVAL = .5
ELEV_DIST_INTERVAL = .2

# Main function
def getOptimalRoute(source, destination):
	# Call Maps URL
	mapsURL = "http://maps.googleapis.com/maps/api/directions/json?origin=" + source + "&destination=" + destination + "&sensor=false&units=metric&alternatives=true&mode=bicycling"
	mapsAPI_responseJSON = json.loads(requests.post(mapsURL, None).text)

	num_routes = len(mapsAPI_responseJSON["routes"])

	if num_routes == 1:
		return [mapsAPI_responseJSON["routes"][0]["overview_polyline"]["points"],0]

	# Logic - Maps API will provide us with redundant number of poly points between source and destination (excluding these)
	# We select some poly points from these set with minimum distance between them as set by constants above
	#
	wind_threads = []
	elev_threads = []
	for routeNum in xrange(num_routes):
		lat_long_arr = []

		# Adding source and destination points
		lat_long_arr.append((mapsAPI_responseJSON["routes"][routeNum]["legs"][0]["start_location"]["lat"],
							mapsAPI_responseJSON["routes"][routeNum]["legs"][0]["start_location"]["lng"]))
		lat_long_arr = polyline.decode(mapsAPI_responseJSON["routes"][routeNum]["overview_polyline"]["points"])
		lat_long_arr.append((mapsAPI_responseJSON["routes"][routeNum]["legs"][0]["end_location"]["lat"],
							mapsAPI_responseJSON["routes"][routeNum]["legs"][0]["end_location"]["lng"]))

		# Maintain separate arrays for wind and elevation threads
		threadName = "thread_" + str(routeNum) + "_wind"
		threadName = windUtil.getWindDataThread(lat_long_arr, WIND_DIST_INTERVAL, routeNum, threadName)
		wind_threads.append(threadName)
		threadName.start()

		threadName = "thread_" + str(routeNum) + "_elev"
		threadName = elevUtil.getElevDataThread(lat_long_arr, ELEV_DIST_INTERVAL, routeNum, threadName)
		elev_threads.append(threadName)
		threadName.start()

	# Joining threads
	for thread in wind_threads + elev_threads:
		thread.join()

	# Storing the cost of each route based on the wind of the path
	costArr = [0. for i in xrange(len(wind_threads))]

	for i in xrange(len(wind_threads)):
		costArr[i] += windCost(wind_threads[i].get())
	wind_result = getComparision(costArr, mapsAPI_responseJSON)

	# Storing the cost of each route based on the elevation of the path
	costArr = [0. for i in xrange(len(wind_threads))]

	for i in xrange(len(elev_threads)):
		costArr[i] += elevCost(elev_threads[i].get())
	elev_result = getComparision(costArr, mapsAPI_responseJSON)

	# Combining both the costs
	result = []
	for i in xrange(len(wind_result)):
		result.append([wind_result[i][0], wind_result[i][1] + elev_result[i][1]])

	# Make first value after sorting to zero to remove the residual value
	result = sorted(result, key=lambda x:x[1])
	result[0][1] = 0.
	# print result
	return result

# Gives the percentage of extra work that needs to be done for paths compared to the optimal path
def getComparision(costArr, mapsAPI_responseJSON):
	min_cost = float("inf")
	min_threadId = 0
	result = []
	for i in xrange(len(costArr)):
		if costArr[i] < min_cost:
			min_cost = costArr[i]
			min_threadId = i

	result = []
	for i in xrange(len(costArr)):
		if costArr[i] < min_cost:
			result.append((mapsAPI_responseJSON["routes"][i]["overview_polyline"]["points"], 0.))
		else:
			result.append((mapsAPI_responseJSON["routes"][i]["overview_polyline"]["points"], ((costArr[i]-min_cost)/min_cost)*100))
	return result

if __name__ == '__main__':
	source = "1265 E University Dr"
	destination = "Scottsdale"

	if source != None and destination != None:
		getOptimalRoute(source, destination)
	else:
		pass
