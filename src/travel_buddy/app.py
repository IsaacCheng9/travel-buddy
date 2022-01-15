import os

from flask import Flask, request, session, redirect

import travel_buddy.views.register as register
import travel_buddy.views.login as login

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "db.sqlite3")

app = Flask(__name__)
app.register_blueprint(register.register_blueprint, url_prefix="")
app.register_blueprint(login.login_blueprint, url_prefix="")

app.url_map.strict_slashes = False
app.secret_key = (
    "i09kd0owe671gdyfjkzmpaopmrionfkwep]l[';fkvfoiejiojd1u232e23fkeorincuiwkdu"
)


@app.route("/")
def hello_world():
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)
