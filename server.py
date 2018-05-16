#!/usr/bin/env python

import json
import stalker

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
    stalker.function(data)
    print('finish')
    return jsonify({'result': len(data)})


if __name__ == '__main__':
    app.run(host='0.0.0.0')
