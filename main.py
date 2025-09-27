

from flask import Flask
app = Flask(__name__)


@app.route('/')
def index():
    return 'Welcome to the anti-furry forums!'


app.run('0.0.0.0', 80, False)
