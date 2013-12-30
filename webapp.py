from flask import Flask, render_template, url_for, request
from whatspy import Whatspy
app = Flask(__name__)

from reverse_image import ReverseImageSearcher
image_searcher = None

@app.route('/')
def index():
    return render_template('purple.html')

@app.route('/view', methods=['POST'])
def view():
    whatspy = Whatspy()
    phone_number = request.form['phone_number']

    # note: photo_path/last_time can be None
    photo_path, last_time = whatspy.get_photo_time(phone_number)

    return render_template('results.html', photo_path=photo_path, phone_number=phone_number)

@app.route('/reverse_image/<local_image_path>')
def reverse_image(local_image_path):
    endpoint_url = url_for("get_reverse_image_results", local_image_path=local_image_path)
    return render_template('reverse_image.html', endpoint_url=endpoint_url)

@app.route('/get_reverse_image_results/<local_image_path>')
def get_reverse_image_results(local_image_path):
    global image_searcher
    if image_searcher is None:
        image_searcher = ReverseImageSearcher()

    return image_searcher.get_results(local_image_path)

# Fire up the server
if __name__ == '__main__':
    app.run(debug=True)
