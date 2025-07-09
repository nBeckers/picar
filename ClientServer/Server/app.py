import os
from flask import Flask, render_template, Response, request, send_from_directory, jsonify


app = Flask(__name__)



@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


if __name__ == '__main__':

    app.run(debug=False, host='0.0.0.0', port=5000)



