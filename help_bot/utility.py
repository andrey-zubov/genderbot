import logging
from time import perf_counter


def check_input(string: str) -> bool:
    """ Do i need to check all inputs?! Usability for others?! """
    if string:
        return True
    return False


def try_except(foo):
    """ Handle exceptions in a selected function = foo_name. """

    def wrapper(*args, **kwargs):
        try:
            return foo(*args, **kwargs)
        except Exception as ex:
            logger = logging.getLogger(__name__)
            logger.error("\tException in - %s()\n\t%s" % (foo.__name__, ex))
            return None

    return wrapper


def time_it(foo):
    """ Return the value (in fractional seconds) of a performance counter for a function = foo_name. """

    def wrapper(*args, **kwargs):
        time_0 = perf_counter()
        print("%s()" % foo.__name__)
        result = foo(*args, **kwargs)
        print('\t%s() - OK; TimeIt: %.6f sec.' % (foo.__name__, perf_counter() - time_0))
        return result

    return wrapper
