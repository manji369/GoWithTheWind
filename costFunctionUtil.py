import math
import decimal
#import radians, cos, sin, asin, sqrt

PRESSURE_CONSTANT = 0.613
SURFACE_AREA = 0.302
DRAG_COEFFICIENT = 1.4

AVG_MASS = 80

# Returns the wind cost integrated over the entire path (F = A*P*Cd, P = 0.613V^2)
def windCost(polyPointList):
	windWorkDone = 0.
	for i in range(1,len(polyPointList)):
		prevPoint = polyPointList[i-1]
		currPoint = polyPointList[i]
		diff_theta = (currPoint.wind['deg'] - decimal.Decimal(calculate_initial_compass_bearing(prevPoint.coord,currPoint.coord)))
		pressure = PRESSURE_CONSTANT * float(currPoint.wind['speed']) * float(currPoint.wind['speed'])
		windForce = SURFACE_AREA * pressure * DRAG_COEFFICIENT
		windWorkDone += windForce * float(currPoint.dist)
	print windWorkDone
	return windWorkDone

# Returns the elevation cost integrated over the entire path (mgsin(theta)*distance)
def elevCost(polyPointList):
	elevWorkDone = 0.
	for i in range(1,len(polyPointList)):
		prevPoint = polyPointList[i-1]
		currPoint = polyPointList[i]
		diff_theta = math.atan((currPoint.elev - prevPoint.elev)/(currPoint.dist*1609.34))
		# print "math.sin(diff_theta) = " + str(math.sin(diff_theta))
		elevForce = AVG_MASS * math.sin(diff_theta)
		# print "elevForce = " + str(elevForce)
		elevWorkDone += elevForce * float(currPoint.dist) * 1609.34
	print elevWorkDone
	return elevWorkDone

# Get the bike travel direction (bearing => North and moving anti-clockwise)
def calculate_initial_compass_bearing(pointA, pointB):
  
	lat1 = math.radians(pointA["lat"])
	lat2 = math.radians(pointB["lat"])

	diffLong = math.radians(pointB["lon"] - pointB["lon"])

	x = math.sin(diffLong) * math.cos(lat2)
	y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1)* math.cos(lat2) * math.cos(diffLong))

	initial_bearing = math.atan2(x, y)
	initial_bearing = math.degrees(initial_bearing)
	compass_bearing = (initial_bearing + 360) % 360

	return compass_bearing