import importlib
import importlib.util
import logging
import os
import platform
import re
import subprocess
import sys
import time
from contextlib import contextmanager
from importlib import import_module as im
from multiprocessing import Process

from packaging import version

LOGGER = logging.getLogger(__name__)

IS_WINDOWS = platform.system() == "Windows"

if IS_WINDOWS:
    import msvcrt
    getche = msvcrt.getche
else:
    import getch
    getche = getch.getche


@contextmanager
def working_directory(path):
    """Context manager to run all code under it in a certain directory

    Args:
        path (str): The path to switch to for the scope of the context manager
    """
    owd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(owd)


def init_logging(level=logging.INFO, filename=None, filemode=None):
    """Set a logging.basicConfig's format to '%(asctime)s [%(levelname)s] %(message)s' and set a certain level

    Args:
        level (int, optional): Logging level. Defaults to logging.INFO.
        filename (str, optional): File to log to. Defaults to None.
        filemode (str, optional): File mode to use. Defaults to None.
    """
    logging.basicConfig(filename=None, filemode=None,
                        format='%(asctime)s [%(levelname)s] %(message)s', force=True)
    logging.getLogger().setLevel(level)


def capitalize_each_word(s, delimiter):
    """Capitalize each word seperated by a delimiter

    Args:
        s (str): The string to capitalize each word in
        delimiter (str): The delimeter words are separated by

    Returns:
        str: The modified string
    """
    return delimiter.join([w.capitalize() for w in s.split(delimiter)])


def strip_each_line(s):
    """Strips each line of a string

    Args:
        s (str): The string to strip each line of

    Returns:
        str: The modified string
    """
    return "\n".join([line.strip() for line in s])


def y_to_continue(prompt="Enter y to continue:", requires_enter=False):
    """Return True if the user enters "y" else False

    Args:
        prompt (str, optional): The prompt to display to the user. Defaults to "Enter y to continue:".
        requires_enter (bool, optional): If this prompt requires the user to hit enter. Defaults to False.

    Returns:
        bool: If the user entered True
    """
    print(prompt + " ", end="", flush=True)
    if not requires_enter:
        y = getche().lower() == "y"
        print()
    else:
        y = input().lower() == "y"
    return y


def input_multiline(warn=None, default=""):
    """Get multiline user input until EOF is reached

    Args:
        warn (str, optional): Warn the user with this message if the input is empty. Defaults to None.
        default (str, optional): Default input to use if no input is read. Defaults to "".

    Returns:
        string: The string inputted
    """
    s = sys.stdin.read()
    s = s.strip()
    if not s.endswith("\n") or not s:
        print()
    if not s:
        if warn is not None:
            LOGGER.warning(warn)
        s = default
    return s


def exception_to_dict(error):
    """Takes in an exception and outputs its details, excluding the stacktrace, to a dict

    Args:
        error (Exception): The exception to serialize

    Returns:
        dict: The serialized exception
    """
    return {"type": str(type(error).__name__), "message": str(error)}


def search_list_of_objs(objs, attr, value):
    """Searches a list of objects and retuns those with an attribute that meets an equality criteria

    Args:
        objs (list): The input list
        attr (str): The attribute to match
        value (any): The value to be matched

    Returns:
        list[any]: The list of objects found
    """
    return [obj for obj in objs if getattr(obj, attr) == value]


def truncate(s, length=25, elipsis=True):
    """Truncates a string. You can specify the length and to exclude the ending elipsis

    Args:
        s (str): The input string
        length (int, optional): The max length of the truncated string. Defaults to 25.
        elipsis (bool, optional): If an elipsis should be appended to the truncated string, if it is actually truncated. Defaults to True.

    Returns:
        str: The truncated string
    """
    if elipsis:
        test_length = length + 3
    else:
        test_length = length
    if len(s) > test_length:
        truncated = s[:length].strip()
        return truncated + "..." if elipsis else truncated
    else:
        return s


@contextmanager
def dummy_context_manager(*args, **kwargs):
    """Useless context manager"""
    yield


@contextmanager
def loading_animation(phrase="Loading...", bar_length=5, completed_success_string="✔", completed_failure_string="✗"):
    """Run a function with a laoding animation. This is the context manager implementation"""
    p = Process(target=_show_loading_animation, args=(phrase, bar_length))
    p.daemon = True
    p.start()
    exc = None
    c = completed_failure_string
    try:
        yield
        c = completed_success_string
    except Exception as e:
        exc = e
    finally:
        p.terminate()
        sys.stdout.write(f"\33[2K\r{phrase} {c}")
        print()
        if exc:
            raise exc


def run_with_loading(function, args=[], kwargs={}, phrase="Loading...", bar_length=5, completed_success_string="✔", completed_failure_string="✗", evaluate_function=None, raise_exc=True):
    '''
    Run a function with a loading animation displayed at the same time. Uses multiprocessing to achieve this. Returns a tuple consisting of the function's return value and a boolean.

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
    """Show a loading animation until killed. Probably only useful if used in multithreading/multiprocessing

    Args:
        phrase (str): Phrase to emit during loading
        bar_length (int): The length of the loading bar
    """
    while True:
        for i in range(bar_length):
            sys.stdout.write(
                f"\r{phrase} {'□' * i}{'■'}{'□' * (bar_length - i - 1)}")
            time.sleep(0.15)
            sys.stdout.flush()


def get_dpkg_package_version(package_name):
    """Get the version of an installed package.

    Args:
        package_name (str): The package name

    Returns:
        str: The version of the package
    """
    return re.findall(r"(?<=Version: ).+", subprocess.check_output(["dpkg", "-s", package_name]).decode())[0]


def check_github_for_newer_versions(app_name, current_version, force_close=sys.exit, force_close_args=[], force_close_kwargs={}):
    """Check GitHub's releases page to see if there is a newer version. Warn or close the program if there is. Reads /etc/ghinfo/{app_name} to get the GitHub repo info

    Args:
        app_name (str): What folder to read the GitHub info from
        current_version (str): The current version of the app
        force_close (Union[bool, function], optional): Callable to close the app with. True means use sys.exit(1). False means do not force close the app. Defaults to sys.exit.
        force_close_args (list[any], optional): List of arguments to pass to the force_close callable. Defaults to [].
        force_close_kwargs (dict, optional): List of keyword arguments to pass to the force_close callable. Defaults to {}.

    Raises:
        ValueError: If an incorrect combo of args is passed
    """
    if (force_close_args or force_close_kwargs) and (not force_close or force_close is True):
        raise ValueError(
            "Cannot specify this combination of force_close, force_close_args, and force_close_kwargs")
    if current_version == "dev":
        return
    filename = os.path.join(os.sep, "etc", "ghinfo", app_name)
    with open(filename) as f:
        repo_owner, repo_name = [l.strip() for l in f.readlines()]
    out = subprocess.check_output(
        ["gh", "release", "list", "-R", f"{repo_owner}/{repo_name}"]).decode().strip()
    latest_version = [l.split("\t", 1)[0] for l in out.split("\n")][0]
    if version.parse(latest_version) > version.parse(current_version):
        if force_close:
            log_function = "critical"
        else:
            log_function = "warning"
        getattr(LOGGER, log_function)(
            f"You are using version {current_version}, but {latest_version} is available on GitHub")
        if force_close:
            LOGGER.critical("Please update to continue using this application")
            if force_close is True:
                sys.exit(1)
            else:
                force_close(*force_close_args, **force_close_kwargs)
        else:
            LOGGER.warning(
                "Please consider upgrading for the latest features and bugfixes")


def get_module_from_filename(path_to_file):
    """Get a module by path

    Args:
        path_to_file (str): Path to the module
        name (str): Name of module

    Raises:
        ModuleNotFoundError: If the module cannot be found

    Returns:
        module: The module
    """
    module_name = path_to_file.split(os.sep)[-1]
    spec = importlib.util.spec_from_file_location(module_name, path_to_file)
    try:
        m = importlib.util.module_from_spec(spec)
    except AttributeError:
        raise ModuleNotFoundError("No module at'{}'".format(path_to_file))
    spec.loader.exec_module(m)
    return m


def get_module(module_name, path=None):
    """Get a module by name, and if that doesn't work, get it by specified path. Once retreieved, it's probably a good idea to set a global with it

    Args:
        module_name (str): Name of module
        path (str, optional): Path to module. Defaults to None.

    Raises:
        ModuleNotFoundError: If the module cannot be found

    Returns:
        module: The module
    """
    try:
        return importlib.import_module(module_name)
    except ModuleNotFoundError as e:
        if path is not None:
            msg = "No module named '{}'".format(module_name)
            if str(e) == msg:
                try:
                    return get_module_from_filename(path)
                except FileNotFoundError:
                    raise ModuleNotFoundError(msg)
            else:
                raise e
        else:
            raise e


def picker(items, item_name="choice"):
    """A picker for a list of items

    Args:
        items (list[any]): The list to pick from
        item_name (str, optional): A friendly name of what an item is. Defaults to "choice".

    Raises:
        ValueError: If the user enters invalid input

    Returns:
        any: The picked item
    """
    if not items:
        raise ValueError(f"Not a single {item_name} to pick from")
    elif len(items) == 1:
        return items[0]
    for index, item in enumerate(items, start=1):
        print(f"{index}) {item}")
    try:
        choice_index = int(input(f"Select a {item_name}: "))
    except ValueError:
        raise ValueError("Invalid input")
    return items[choice_index - 1]
