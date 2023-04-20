#coding: utf-8
import sys
import os

from flask import Flask, render_template,jsonify,request
from flask import session as fsess
from api_handler import api_handle
app = Flask(__name__)
app.config["DEBUG"] = True

@app.route("/")
def hello():
    return render_template('index.html')

@app.route("/api")
def api_id():
    print(f"got api request {request}")
    response = api_handle(request)
    return jsonify(response)

if __name__ == '__main__': app.run(debug=False,host='0.0.0.0')
