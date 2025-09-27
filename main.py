from flask import Flask

import logging
import waitress
import colorama

from core.utils import config
from core.utils import webhook

app = Flask(__name__)
config_loader = config.ConfigSet()
startup_hook = webhook.available_webhooks["general"]


@app.route("/")
def index():
    return "Welcome to the anti-furry forums!"


def initialize_application(app: Flask):
    """
    Load configs and run the given application
    """

    # hosting configuration loaders
    main_config_file_path = config_loader.main_config_file_path
    port = config_loader.get_value(main_config_file_path, "hosting.port")

    interface = config_loader.get_value(main_config_file_path, "hosting.interface")

    debug = config_loader.get_value(main_config_file_path, "hosting.debug")

    server = config_loader.get_value(main_config_file_path, "hosting.server")

    threads = config_loader.get_value(main_config_file_path, "hosting.threads")

    flask_log = config_loader.get_value(main_config_file_path, "hosting.flask-log")

    # server startup message
    def server_start_message():
        print(
            f"""{colorama.Fore.BLUE} Hosting on 'http://{interface}:{port}' with {threads} server threads. {colorama.Fore.WHITE}"""
        )

        if debug:
            print(
                f"""{colorama.Fore.RED} WARNING: hosting.debug is turned on do not deploy! {colorama.Fore.WHITE}"""
            )

        startup_hook.log_action(
            f"""[Server startup!] Hosting on port '{port}' with {threads} server threads."""
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


if __name__ == "__main__":
    initialize_application(app)
