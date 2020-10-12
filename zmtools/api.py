import logging
from multiprocessing import Process
import platform
import sys
import time

LOGGER = logging.getLogger(__name__)

IS_WINDOWS = platform.system() == "Windows"

if IS_WINDOWS:
    import msvcrt
    getche = msvcrt.getche
else:
    import getch
    getche = getch.getche


def init_logging(level=logging.INFO, filename=None, filemode=None):
    '''
    Set a logging.basicConfig's format to '%(asctime)s [%(levelname)s] %(message)s' and set a certain level.
    '''

    logging.basicConfig(filename=None, filemode=None,
                        format='%(asctime)s [%(levelname)s] %(message)s', force=True)
    logging.getLogger().setLevel(level)


def capitalize_each_word(s, delimiter):
    '''
    Capitalize each word seperated by a delimiter. Returns a string.
    '''

    return delimiter.join([w.capitalize() for w in s.split(delimiter)])


def strip_each_line(s):
    '''
    Strips each line of a string. Returns a string.
    '''

    return "\n".join([line.strip() for line in s])


def y_to_continue(prompt="Enter y to continue:", requires_enter=False):
    '''
    y to return True, else False. Returns a boolean.
    '''

    print(prompt + " ", end="", flush=True)
    if not requires_enter:
        y = getche().lower() == "y"
        print()
    else:
        y = input().lower() == "y"
    return y


def input_multiline(warn="", default=""):
    '''
    Get multiline user input until EOF. Returns a string.
    '''

    s = sys.stdin.read()
    s = s.strip()
    if not s.endswith("\n") or not s:
        print()
    if not s:
        LOGGER.warning(warn)
        s = default
    return s


def exception_to_dict(error):
    '''
    Takes in an exception and outputs its details, excluding the stacktrace, to a dict. Returns a dict.
    '''

    return {"type": str(type(error).__name__), "message": str(error)}


def search_list_of_objs(objs, attr, value):
    '''
    Searches a list of objects and retuns those with an attribute that meets an equality criteria. Returns a list.
    '''

    return [obj for obj in objs if getattr(obj, attr) == value]


def truncate(s, length=25, elipsis=True):
    '''
    Truncates a string. You can specify the length and to exclude the ending elipsis. Returns the truncated string.
    '''

    if elipsis:
        test_length = length + 3
    else:
        test_length = length
    if len(s) > test_length:
        truncated = s[:length].strip()
        return truncated + "..." if elipsis else truncated
    else:
        return s


def run_with_loading(function, args=[], kwargs={}, phrase="Loading...", bar_length=5, completed_success_string="✔", completed_failure_string="✗", evaluate_function=None, raise_exc=True):
    '''
    Run a function with a loading animation displayed at the same time. Uses multiprocessing to achieve this.
    
    evaluate_function must be either a callable that returns True or False to determine if the function that ran succeeded or not, or None, in which case the function will always be treated as if it succeeded
    '''
    p = Process(target=_show_loading_animation, args=(phrase, bar_length))
    p.daemon = True
    p.start()
    try:
        output = function(*args, **kwargs)
        if evaluate_function is None or evaluate_function(output):
            c = completed_success_string
            succeded = True
        else:
            c = completed_failure_string
            succeded = False
        raised_exc = False
    except Exception as e:
        output = e
        c = completed_failure_string
        succeded = False
        raised_exc = True
    p.terminate()
    sys.stdout.write(f"\33[2K\r{phrase} {c}")
    print()
    if raised_exc and raise_exc:
        raise output
    return output, succeded


def _show_loading_animation(phrase, bar_length):
    '''
    Show a loading animation. Probably only useful if used in multithreading/multiprocessing
    '''
    while True:
        for i in range(bar_length):
            sys.stdout.write(
                f"\r{phrase} {'□' * i}{'■'}{'□' * (bar_length - i - 1)}")
            time.sleep(0.15)
            sys.stdout.flush()
