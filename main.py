from flask import Flask
from flask import request
from flask_limiter import Limiter

import logging
import waitress
import colorama

from core.utils import config
from core.utils import log
from core.utils import ip

from core.prequest import track_traffic

app = Flask(__name__)

ratelimiter = Limiter(
    ip.get_real_ip_no_params,
    app=app,
    default_limits=["5 per minute"],
    storage_uri="memory://",
    on_breach=ip.ratelimit_breached
)

config_loader = config.ConfigSet()
startup_logger = log.DataLogger('startup','general').get_logger()

@ratelimiter.limit("80 per minute")
@app.before_request
def before_request():

    real_ip = ip.get_real_ip(
        request
    )

    if ip.is_ip_banned(real_ip):
        track_traffic.log_traffic(request,True)
        return f'<h1>Your ip adress "{real_ip}" is banend for reason "{ip.ip_ban_details(real_ip)[1]}"</h1>',403
    
    
    track_traffic.log_traffic(request,False)

@app.route("/")
def index():
    return "Welcome to the anti-furry forums!"


def load_configs_and_run(app: Flask):
    """
    Load configs and run the given application
    """
    # hosting configuration loaders
    main_config_file_path = config_loader.main_config_file_path
    port = config_loader.get_value(main_config_file_path, "hosting.port")

    interface = config_loader.get_value(
        main_config_file_path, "hosting.interface"
    )

    debug = config_loader.get_value(
        main_config_file_path, "hosting.debug"
    )

    server = config_loader.get_value(
        main_config_file_path, "hosting.server"
    )

    threads = config_loader.get_value(
        main_config_file_path, "hosting.threads"
    )

    flask_log = config_loader.get_value(
        main_config_file_path, "hosting.flask-log"
    )

    # server startup message
    def server_start_message():
        print(
            f"""{colorama.Fore.BLUE} Hosting on 'http://{interface}:{port}'"""
            f""" with {threads} server threads. {colorama.Fore.WHITE}"""
        )

        if debug:
            print(
                f"""{colorama.Fore.RED} WARNING: hosting.debug is turned on """
                f"""do not deploy! {colorama.Fore.WHITE}"""
            )

        startup_logger.info(
            f"""[Server startup!] Hosting on intrface '{interface}' """
            f"""port '{port}' """
            f"""with {threads} server threads."""
        )

    if server == "flask":
        if not flask_log:
            log = logging.getLogger("werkzeug")
            log.disabled = True
        server_start_message()
        app.run(interface, port, debug)
    elif server == "waitress":
        server_start_message()
        waitress.serve(app, listen=f"{interface}:{port}", threads=threads)

def load_blueprints(app: Flask):
    """
    Load all blueprints
    """

    from core.blueprints.api.user import user_blueprint

    app.register_blueprint(user_blueprint,url_prefix="/api/user")

def initialize_application(app: Flask):
    """
    Load everything and run
    """
    
    load_blueprints(app)
    load_configs_and_run(app)

if __name__ == "__main__":
    initialize_application(app)
