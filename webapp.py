from flask import Flask, render_template, url_for, request, redirect, jsonify
from whatspy import Whatspy
from datetime import datetime
import requests, json
app = Flask(__name__)

import reverse_image

from config import AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_BUCKET
from boto.s3.connection import S3Connection

@app.route('/')
def index():
    return render_template('purple.html')

@app.route('/view', methods=['GET', 'POST'])
def view():
    if 'phone_number' not in request.form:
        return redirect(url_for('index'))

    whatspy = Whatspy()
    phone_number = request.form['phone_number']

    # note: photo_path/last_time can be None
    photo_path, last_time = whatspy.get_photo_time(phone_number)

    # parse as a datetime
    if last_time:
      last_time = datetime.strptime(last_time, "%a %b %d %H:%M:%S %Y")

    return render_template('results.html', photo_path=photo_path, last_time=last_time, phone_number=phone_number)

@app.route('/reverse_image/<local_image_path>')
def reverse_image_tester(local_image_path):
    endpoint_url = url_for("get_reverse_image_results", local_image_path=local_image_path)
    return render_template('reverse_image.html', endpoint_url=endpoint_url)

s3_bucket = None

def get_s3_bucket():
    global s3_bucket
    if s3_bucket is None:
        conn = S3Connection(AWS_ACCESS_KEY, AWS_SECRET_KEY)
        s3_bucket = conn.get_bucket(AWS_BUCKET)
    return s3_bucket

@app.route('/get_reverse_image_results/<local_image_path>')
def get_reverse_image_results(local_image_path):
    bucket = get_s3_bucket()
    return reverse_image.get_results(local_image_path, bucket)

@app.route('/timeline', methods=['POST'])
def timeline():
    phone = request.form['phone']
    r = requests.get('http://50.112.143.163/?phone=' + phone)
    return jsonify(json.loads(r.text))

# Fire up the server
if __name__ == '__main__':
    app.run(debug=True)
