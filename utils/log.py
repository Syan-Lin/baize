import os
import logging
from functools import wraps

log_file = 'baize.log'
if os.path.exists(log_file):
    os.remove(log_file)
logging.basicConfig(filename=log_file, level=logging.INFO,
                    format='%(levelname)s - %(funcName)s - %(lineno)d - %(message)s')


def log(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if len(args) == 0:
            logging.info(f"Calling function: `{func.__name__}`")
        else:
            logging.info(f"Calling function `{func.__name__}` with args: {args}")
        result = func(*args, **kwargs)
        if result:
            logging.info(f"Function `{func.__name__}` returned: {result}")
        return result
    return wrapper