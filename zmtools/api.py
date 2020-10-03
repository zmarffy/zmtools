import logging
import platform
import sys

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
