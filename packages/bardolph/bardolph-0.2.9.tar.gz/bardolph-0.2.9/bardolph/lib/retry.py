import functools
import logging
import traceback


def tries(num_tries, ex_type, fail_value=None):
    '''Decorator for retrying a function if a specific type of Exception is
    raised.

    Parameters
    ----------
    num_tries
        Total number of times to try before giving up. Should be >= 2.
    ex_type
        Type of exception that allows a retry. Any other type of exception
        raised by the wrapped function will be unhandled.
    fail_value:
        What value to return after all the tries have been exhausted. Defaults
        to False.

    Returns
    -------
        Whatever the wrapped function returns, or fail_value if the maximum
        number of tries have failed.
    '''
    def fn_wrapper(fn):
        @functools.wraps(fn)
        def retry_wrapper(*args, **kwargs):
            tries_remaining = num_tries
            while tries_remaining > 0:
                try:
                    return fn(*args, **kwargs)
                except ex_type as ex:
                    logging.warning(ex)
                    logging.debug(traceback.format_exc())
                    logging.debug('Tries remaining: {}'.format(tries_remaining))
                    tries_remaining -= 1
            logging.warning('Giving up after {} tries.'.format(num_tries))
            return fail_value
        return retry_wrapper
    return fn_wrapper
