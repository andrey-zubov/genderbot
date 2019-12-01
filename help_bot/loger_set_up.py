import logging


def logger_telegram():
    # create logger with 'spam_application'
    logger = logging.getLogger('telegram_bot')
    logger.setLevel(logging.WARNING)
    # create file handler which logs even debug messages
    fh = logging.FileHandler('telegram_bot.log')
    fh.setLevel(logging.WARNING)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger


def logger_web_chat():
    logger = logging.getLogger('web_chat_bot')
    logger.setLevel(logging.WARNING)
    # create file handler which logs even debug messages
    fh = logging.FileHandler('web_chat_bot.log')
    fh.setLevel(logging.WARNING)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger


def logger_utility():
    logger = logging.getLogger('app_utilities')
    logger.setLevel(logging.WARNING)
    # create file handler which logs even debug messages
    fh = logging.FileHandler('app_utilities.log')
    fh.setLevel(logging.WARNING)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger
