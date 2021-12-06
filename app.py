"""
Main module of the server file
"""

# 3rd party moudles
from flask import render_template

# local modules
import app_config


# Get the application instance
connex_app = app_config.connex_app

# Read the swagger.yml file to configure the endpoints
connex_app.add_api("swagger.yaml", strict_validation=True,
                   pythonic_params=True)


# create a URL route in our application for "/"
@connex_app.route("/")
def home():
    """
    This function just responds to the browser URL
    localhost:5000/

    :return:        the rendered template "home.html"
    """
    return render_template("home.html")


if __name__ == "__main__":
    connex_app.run(debug=True)
