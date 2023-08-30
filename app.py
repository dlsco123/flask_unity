from flask import Flask
from api.routes import myhome_bp
import logging
from flask_cors import CORS

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app)
app.register_blueprint(myhome_bp)

if __name__ == "__main__":
    print("run")
    app.run(debug=True, port=5000)
