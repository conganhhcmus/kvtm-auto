import argparse
from flask import Flask, jsonify
from flask_cors import CORS

from apis.device_apis import device_bp
from apis.execution_apis import execution_bp
from apis.script_apis import script_bp
from apis.system_apis import system_bp

app = Flask(__name__)
CORS(app)


# Register blueprints
app.register_blueprint(device_bp)
app.register_blueprint(script_bp)
app.register_blueprint(execution_bp)
app.register_blueprint(system_bp)


@app.route("/")
def hello_world():
    return jsonify(message="Hello, World!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--env", choices=["dev", "prod"], default="dev", help="Environment: dev or prod"
    )

    args = parser.parse_args()
    if args.env == "dev":
        app.run(host="0.0.0.0", port=3001, debug=True)  # auto reload
    else:
        app.run(host="0.0.0.0", port=3001, debug=False)  # no reload
