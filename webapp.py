from flask import Flask, render_template
import whatspy
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('purple.html')

@app.route('/view')
def view():
    # note: photo_path/last_time can be None
    photo_path, last_time = whatspy.get_photo_time('13104874553')
    return render_template('results.html', photo_path=photo_path)

# Fire up the server
if __name__ == '__main__':
    app.run()
