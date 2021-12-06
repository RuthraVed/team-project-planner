import connexion
from pathlib import Path
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

BASE_DIR = Path.cwd()

# Create the connexion application instance
connex_app = connexion.App(__name__, specification_dir=BASE_DIR)

# Get the underlying Flask app instance
app = connex_app.app

# Build the Sqlite URL for SqlAlchemy
# Build the Sqlite URL for SqlAlchemy
sqlite_url = "sqlite:///" + str(Path(BASE_DIR / "db/team_project_planner.db"))

# Configure the SqlAlchemy part of the app instance
app.config["SQLALCHEMY_ECHO"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = sqlite_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Create the SqlAlchemy db instance
db = SQLAlchemy(app)

# Initialize Marshmallow
ma = Marshmallow(app)
