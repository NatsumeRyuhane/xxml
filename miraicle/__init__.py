from .mirai import Mirai
from .asyncmirai import AsyncMirai
from .message import *
from .filters import *
from .schedule import Scheduler, scheduled_job

import logging

logging.addLevelName(21, "RECEIVED MESSAGE")
def received_message(msg, *args, **kwargs):
    if logging.getLogger().isEnabledFor(21):
        logging.log(21, msg)
logging.received_message = received_message

logging.addLevelName(22, "SEND MESSAGE")
def send_message(msg, *args, **kwargs):
    if logging.getLogger().isEnabledFor(22):
        logging.log(22, msg)
logging.send_message = send_message

logging.warning("Using customized Miraicle framework.")