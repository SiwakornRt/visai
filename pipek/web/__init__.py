import optparse

from flask import Flask

from dotenv import load_dotenv, dotenv_values

from pipek import dashapp
from . import views
from . import caches

from .. import clients
from .. import models


from . import acl
from . import redis_rq

# from . import oauth2


def create_app():
    flask_app = Flask(__name__)
    flask_app.config.from_object("pipek.default_settings")
    flask_app.config.from_envvar("PIPEK_SETTINGS", silent=True)

    load_dotenv()
    flask_app.config.update(dotenv_values(".env"))

    views.register_blueprint(flask_app)
    caches.init_cache(flask_app)

    models.init_db(flask_app)
    redis_rq.init_rq(flask_app)

    # oauth2.init_oauth(flask_app)
    acl.init_acl(flask_app)

    dashapp.init_dash(flask_app)
    return flask_app


def get_program_options(default_host="127.0.0.1", default_port="8080"):
    """
    Takes a flask.Flask instance and runs it. Parses
    command-line flags to configure the app.
    """

    # Set up the command-line options
    parser = optparse.OptionParser()
    parser.add_option(
        "-H",
        "--host",
        help="Hostname of the Flask app " + "[default %s]" % default_host,
        default=default_host,
    )
    parser.add_option(
        "-P",
        "--port",
        help="Port for the Flask app " + "[default %s]" % default_port,
        default=default_port,
    )

    # Two options useful for debugging purposes, but
    # a bit dangerous so not exposed in the help message.
    parser.add_option(
        "-c", "--config", dest="config", help=optparse.SUPPRESS_HELP, default=None
    )
    parser.add_option(
        "-d", "--debug", action="store_true", dest="debug", help=optparse.SUPPRESS_HELP
    )
    parser.add_option(
        "-p",
        "--profile",
        action="store_true",
        dest="profile",
        help=optparse.SUPPRESS_HELP,
    )

    options, _ = parser.parse_args()

    return options
