# adapted from the code by Steven J. Bethard <steven.bethard@gmail.com>
# in the Python standard library tests (cpython/lib/test/test_argparse.py)
# under the Python license

import sys
from io import StringIO


class StdIOBuffer(StringIO):
    pass


class ArgumentParserError(Exception):

    def __init__(self, message, stdout=None, stderr=None, error_code=None):
        Exception.__init__(self, message, stdout, stderr)
        self.message = message
        self.stdout = stdout
        self.stderr = stderr
        self.error_code = error_code


def stderr_to_parser_error(parse_args, *args, **kwargs):
    # if this is being called recursively and stderr or stdout is already being
    # redirected, simply call the function and let the enclosing function
    # catch the exception
    if isinstance(sys.stderr, StdIOBuffer) or isinstance(sys.stdout, StdIOBuffer):
        return parse_args(*args, **kwargs)

    # if this is not being called recursively, redirect stderr and
    # use it as the ArgumentParserError message
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = StdIOBuffer()
    sys.stderr = StdIOBuffer()
    try:
        try:
            result = parse_args(*args, **kwargs)
            for key in list(vars(result)):
                if getattr(result, key) is sys.stdout:
                    setattr(result, key, old_stdout)
                if getattr(result, key) is sys.stderr:
                    setattr(result, key, old_stderr)
            return result
        except SystemExit:
            code = sys.exc_info()[1].code
            stdout = sys.stdout.getvalue()
            stderr = sys.stderr.getvalue()
            raise ArgumentParserError("SystemExit", stdout, stderr, code)
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr

