from flask import Flask
from .saves.routes import saves_bp
from .upload.routes import upload_bp


def create_app():
    app = Flask(__name__)

    app.register_blueprint(saves_bp)
    app.register_blueprint(upload_bp)

    @app.route("/", methods=["GET"])
    def get_root():
        return "Racine du serveur."

    return app
