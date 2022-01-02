from flask import Flask, request, session

import travel_buddy.views.register as register

app = Flask(__name__)
app.url_map.strict_slashes = False
app.register_blueprint(register.register_blueprint, url_prefix="")
app.secret_key = (
    "i09kd0owe671gdyfjkzmpaopmrionfkwep]l[';fkvfoiejiojd1u232e23fkeorincuiwkdu"
)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


if __name__ == "__main__":
    app.run(debug=True)
