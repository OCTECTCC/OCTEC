import os
from dotenv import load_dotenv
from app import create_app, db

load_dotenv()

config_object = os.getenv("FLASK_CONFIG", "app.config.Config")

app = create_app(config_object=config_object)

if os.getenv("CREATE_DB_ON_START", "True").lower() in ("1", "true", "yes"):
    with app.app_context():
        db.create_all()

if __name__ == "__main__":
    app.run(debug=app.config.get("DEBUG", True))