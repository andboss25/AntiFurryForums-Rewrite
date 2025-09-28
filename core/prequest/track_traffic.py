
import flask
from core.utils import log
from core.utils import ip

logger = log.DataLogger('traffic','').get_logger()

def log_traffic(request: flask.Request):
    real_ip = ip.get_real_ip(request)
    
    logger.info(f"{real_ip} - {request.path}")
