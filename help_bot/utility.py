from time import perf_counter

from help_bot.loger_set_up import logger_utility


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
            logger_utility().exception("Exception in - %s():\n\t%s" % (foo.__name__, ex))
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
