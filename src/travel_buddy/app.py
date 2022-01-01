from flask import Flask, request, session

import travel_buddy.views.register as register

app = Flask(__name__)
app.url_map.strict_slashes = False
app.register_blueprint(register.register_blueprint, url_prefix="")


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"
