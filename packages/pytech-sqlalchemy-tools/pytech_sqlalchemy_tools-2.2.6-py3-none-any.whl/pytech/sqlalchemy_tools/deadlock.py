from functools import wraps
from time import sleep

from sqlalchemy.exc import OperationalError

from pytech.sqlalchemy_tools.logger import logger_handler

logger = logger_handler.get_logger(__name__)


LOCK_MESSAGE_ERROR = "database is locked"
MAX_RETRY_ON_DEADLOCK = 3


def retry_on_deadlock(max_retries=MAX_RETRY_ON_DEADLOCK, sleep_time=1):
    """
    Retry the execution of a function if a deadlock is detected.

    :param max_retries: the number of times to retry the function
    :param sleep_time: time to wait between retries
    :return: the decorator
    """

    def decorator(func):
        """
        The actual decorator

        :param func: The function to decorate
        :return:
        """

        @wraps(func)
        def wrapper(*args, **kwargs):
            """
            The wrapped function
            :param args:
            :param kwargs:
            :return:
            """
            attempt_count = 0
            while attempt_count < max_retries:
                attempt_count += 1
                try:
                    return func(*args, **kwargs)
                except OperationalError as e:
                    if e._message != LOCK_MESSAGE_ERROR and attempt_count < max_retries:
                        logger.warning(
                            f"DB lock detected while executing {func.__name__}. "
                            f"Attempt {attempt_count} of {max_retries}."
                        )
                        logger.debug(f"args: {args} - kwargs: {kwargs}")
                        sleep(sleep_time)
                    else:
                        logger.error(
                            f"DB lock still present after {max_retries} attempts "
                            f"in the execution of {func.__name__}."
                        )
                        logger.debug(f"args: {args} - kwargs: {kwargs}")
                        raise
            return None

        return wrapper

    return decorator
