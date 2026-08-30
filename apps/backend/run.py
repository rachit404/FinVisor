from app import create_app
from flask_cors import CORS


app = create_app()


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=8000,
        debug=app.config["DEBUG"],
    )
    CORS(app)