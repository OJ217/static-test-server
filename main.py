from flask import Flask
from flask_cors import CORS

from endpoints import st_api

def create_app() -> Flask:
    """
    Application factory for the static test server.
    """
    app = Flask(__name__)
    CORS(app)
    app.register_blueprint(st_api, url_prefix="/api")
    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
