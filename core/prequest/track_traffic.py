
import flask
from core.utils import log
from core.utils import ip

logger = log.DataLogger('traffic','').get_logger()

def log_traffic(request: flask.Request,blocked:bool):
    real_ip = ip.get_real_ip(request)

    if blocked:
        logger.info(f"[BLOCKED {real_ip}] - {request.path}")
        return
    
    logger.info(f"{real_ip} - {request.path}")