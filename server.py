#!/usr/bin/env python

import json
from stalker import *

from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/stalker', methods=['POST'])
@cross_origin()
def run():
    data = json.loads(request.get_data())
    print('start')
    FM = stalker_evolution(stalker_graph(data))
    print('continue...')
    stalker_plot(FM, "eigenvector")
    stalker_plot(FM, "closeness")
    stalker_plot(FM, "betweenness")
    print('finish')
    return jsonify({'result': len(data)})


@app.route('/test', methods=['GET'])
@cross_origin()
def test():
    return jsonify({'State': 'OK'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
