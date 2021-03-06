from flask import Flask, render_template, url_for, request, redirect, jsonify, abort
from whatspy import Whatspy
from datetime import datetime
import time
import requests, json
app = Flask(__name__)

import reverse_image
import facebook

from config import AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_BUCKET, FACEBOOK_APP_CREDS, FLASK_HOST, FLASK_PORT
from boto.s3.connection import S3Connection

@app.route('/')
def index():
    return render_template('purple.html')

@app.route('/view', methods=['GET', 'POST'])
def view():
    if 'phone_number' not in request.form:
        return redirect(url_for('index'))
    phone_number = request.form['phone_number']

    return render_template('results.html', phone_number=phone_number)

@app.route('/ajax/whatsapp', methods=['POST'])
def whatsapp_endpoint():
    phone_number = request.form['phone_number']
    whatspy = Whatspy()

    # note: photo_path/last_time can be None
    photo_path, last_time = whatspy.get_photo_time(phone_number)

    # parse as a datetime
    if last_time:
        last_time = datetime.strptime(last_time, "%a %b %d %H:%M:%S %Y")
        last_time = time.mktime(last_time.timetuple())

    if photo_path is None and last_time is None:
        abort(404)

    data = dict(
        photo_path = photo_path,
        last_time = last_time,
    )
    return json.dumps(data)

@app.route('/demo/reverse_image/<local_image_path>')
def reverse_image_tester(local_image_path):
    return render_template('reverse_image.html', local_image_path=local_image_path)

s3_bucket = None

def get_s3_bucket():
    global s3_bucket
    if s3_bucket is None:
        conn = S3Connection(AWS_ACCESS_KEY, AWS_SECRET_KEY)
        s3_bucket = conn.get_bucket(AWS_BUCKET)
    return s3_bucket

@app.route('/ajax/reverse_image', methods=['POST'])
def reverse_image_endpoint():
    local_image_path = request.form['local_image_path']
    bucket = get_s3_bucket()
    return reverse_image.get_results(local_image_path, bucket)

@app.route('/timeline', methods=['GET'])
def timeline():
    phone = request.args['phone']
    r = requests.get('http://50.112.143.163/?phone=' + phone)
    if r.status_code == 404:
        abort(404)
    raw = json.loads(r.text)
    stuff = {"data":map(lambda x: int(float(x)), raw["data"]), "number":int(raw["number"])}
    return jsonify(stuff)

@app.route('/ajax/facebook', methods=['POST'])
def facebook_endpoint():
    phone_number = request.form['phone_number']
    fbid = facebook.lookup_facebook_by_phone(phone_number)
    if fbid is None:
        abort(404)

    # get fb info
    token = FACEBOOK_APP_CREDS['app_id'] + '|' + FACEBOOK_APP_CREDS['app_secret']
    url = 'https://graph.facebook.com/' + str(fbid) + '?key=value&access_token=' + token
    req = json.loads(requests.get(url).text)

    # get fb profile picture
    pic_url = 'https://graph.facebook.com/' + str(fbid) + '/picture?redirect=false&width=400&key=value&access_token=' + token
    pic_req = json.loads(requests.get(pic_url).text)

    # combine in dict
    d = dict(req)
    try:
        d.update({'url':pic_req['data']['url']})
    except:
        pass

    return jsonify(d)

# Fire up the server
if __name__ == '__main__':
    app.run(debug=True, host=FLASK_HOST, port=FLASK_PORT)
