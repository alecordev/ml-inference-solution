import sys
import datetime
import traceback


def now():
    return datetime.datetime.utcnow()


def log(msg):
    print(f"[{now().isoformat()}] {msg}")


def get_exception_details(num=-1):
    exc_type, exc_value, exc_traceback = sys.exc_info()
    exception_string = "".join(traceback.format_exception_only(exc_type, exc_value))
    (filename, line_number, function_name, text) = traceback.extract_tb(exc_traceback)[
        num
    ]

    error = {
        "type": str(exc_type.__name__),
        "value": str(exc_value),
        "message": exception_string,
        "location": {
            "filename": filename,
            "lineno": line_number,
            "function_name": function_name,
            "line": text,
        },
    }
    return error
