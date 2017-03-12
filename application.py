#!flask/bin/python
from flask import Flask ,jsonify
from main import getOptimalRoute

application = Flask(__name__)

@application.route('/<string:r>', methods=['GET'])
def index(r):
    print r
    [start, destination] = r.split('&')
    polyL = getOptimalRoute(start, destination)
    return jsonify({"points": [start, destination], "distance": "25", "windText": "Wind will oppose you for 50 % of ride", "climate": "sunny", "polyline": polyL})

if __name__ == '__main__':
    application.run(debug=True)
