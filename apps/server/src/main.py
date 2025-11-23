import argparse

from flask import Flask, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO

from apis.device_apis import device_bp
from apis.execution_apis import execution_bp
from apis.script_apis import script_bp
from apis.stream_apis import stream_bp, init_stream_handlers
from apis.system_apis import system_bp

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize SocketIO with CORS support
# Using threading mode for better compatibility (eventlet has issues with Python 3.13+)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')


# Register blueprints
app.register_blueprint(device_bp)
app.register_blueprint(script_bp)
app.register_blueprint(execution_bp)
app.register_blueprint(stream_bp)
app.register_blueprint(system_bp)

# Initialize Socket.IO stream handlers
init_stream_handlers(socketio)


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
        socketio.run(app, host="0.0.0.0", port=3001, debug=True)  # auto reload
    else:
        # Production mode - use socketio.run with production settings
        print("Starting KVTM Auto Server in production mode...")
        print("Server will be available at http://0.0.0.0:3001")
        socketio.run(
            app,
            host="0.0.0.0",
            port=3001,
            debug=False,
            use_reloader=False,
            log_output=True,
            allow_unsafe_werkzeug=True  # Required for Flask-SocketIO threading mode
        )
