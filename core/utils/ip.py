"""Ip adress util"""

try:
    from core.utils import config
except ModuleNotFoundError:
    import config

try:
    from core.utils import log
except ModuleNotFoundError:
    import log

import flask

config_loader = config.ConfigSet()
logger = log.DataLogger("ip-util-anomaly","anomaly").get_logger()

forward_ip_header = config_loader.get_value(
    config_loader.main_config_file_path,
    "reverse-proxy.real-ip-header"
)

forward_ip_enabled = False

if forward_ip_header != '':
    forward_ip_enabled = True

def get_real_ip(request: flask.Request) -> str:
    """Get the real ip adress taking into account reverse proxies and such"""
    
    if not forward_ip_enabled:
        return request.remote_addr
    
    if request.headers.get(forward_ip_header) is not None:
        return request.headers.get(forward_ip_header)
    else:
        logger.exception("'reverse-proxy.real-ip-header' exists but a request didnt provide such header. Returned the normal ip.")
        return request.remote_addr

# idk how to test this