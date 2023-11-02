import logging

logging.addLevelName(21, "MSGRECV")


def received_message(msg, *args, **kwargs):
    if logging.getLogger().isEnabledFor(21):
        logging.log(21, msg)


logging.received_message = received_message

logging.addLevelName(22, "MSGSEND")


def send_message(msg, *args, **kwargs):
    if logging.getLogger().isEnabledFor(22):
        logging.log(22, msg)


logging.send_message = send_message
