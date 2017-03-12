Objective: To build a custom navigation app for bikers
What we dreamt of: An application that suggests cyclists the best route to take from a source to destination based on factors like wind and slope. 
What we have built: A web app that takes a source and destination as input and calculates the predicted workdone by wind and gravity on the cyclist for different routes and displays the route with minimum workdone by using openweathermapapi and google maps elevation api. Backend processing was done in python and a flask server was setup to communicate between the web app (front end javascript) and backend python. Once the results obtained, front end displays the best route over a map obtained from google maps api and a value for each of the routes relative to optimal route.

Run application.py for python flask server and open localindex.html to start using the app.
