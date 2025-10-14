import argparse
from hashlib import sha256
from http.cookies import SimpleCookie
import datetime
import os
import pickle
import signal
import sys
import tempfile
import typing
import re
import shutil

import requests
from requests_toolbelt.utils import dump

from ptlibs import ptdefs
from ptlibs.ptprinthelper import out_if, ptprint

#from ptlibs import cachefile
from ptlibs.app_dirs import AppDirs

def read_file(file: str) -> list[str]:
    with open(file, "r") as f:
        domain_list = [line.strip("\n") for line in f]
        return domain_list

def pairs(pair):
    if len(pair.split(":")) == 2:
        return pair
    else:
        raise ValueError('Not a pair')

def parse_range(string: str):
    """Parses range, expected formats are 1-999999, 1 9999"""
    match = re.match(r'(\d+)[- ](\d+)$', string)
    try:
        if not match:
            raise argparse.ArgumentTypeError(f"Error: {string} is invalid range format. Expected range format: 1-99999 or 1 99999.")
        if int(match.group(1)) > int(match.group(2)):
            raise argparse.ArgumentTypeError(f"Error: Provided range is not valid")
        if (int(match.group(1)) > 99999) or (int(match.group(2)) > 99999):
            raise argparse.ArgumentTypeError(f"Error: Provided range is too high")

        if int(match.group(1)) < 1:
            return ( 1, int(match.group(2)) )
        return ( int(match.group(1)), int(match.group(2)) )

    except argparse.ArgumentTypeError as e:
        print(e)
        sys.exit(1)
        return (1, 10)


def get_wordlist(file_handler, begin_with=""):
    while True:
        data = file_handler.readline().strip()
        if not data:
            break
        if data.startswith(begin_with):
            yield data


def time2str(time):
    return str(str(datetime.timedelta(seconds=time))).split(".")[0]


def save_object(obj: dict,  filename) -> None:
    with open(os.path.join(get_penterep_temp_dir(), filename), "wb") as output_file:
        pickle.dump(obj, output_file, pickle.HIGHEST_PROTOCOL)


def load_object(filename) -> object:
    with open(os.path.join(get_penterep_temp_dir(), filename), "rb") as input_file:
        return pickle.load(input_file)


def exists_temp(filename: str) -> bool:
    """Checks whether a file exists in tmp and is created in the last day

    Args:
        filename (str): name of the file

    Returns:
        bool: True if the file exists and is created in the last day
    """

    #check if file exists in tmp
    if not os.path.isfile(os.path.join(get_penterep_temp_dir(), filename)):
        return False

    #check if file is created in the last day
    file_older_than_day = get_file_modification_age(filename).days > 1
    if file_older_than_day:
        os.remove(os.path.join(get_penterep_temp_dir(), filename))
        return False
    else:
        return True


def get_file_modification_age(filename: str) -> datetime.timedelta:
    return (datetime.datetime.now() - datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(get_penterep_temp_dir(), filename))))


def get_temp_filename_from_url(url: str, method: str, headers: dict) -> str:
    input_bytes = (url + method + str(headers)).encode()
    return sha256(input_bytes).hexdigest()


def get_response_data_dump(response: requests.models.Response) -> dict:
    """Returns a dictionary containing dump of response data from provided response object

    Args:
        response (requests.models.Response): response object

    Returns:
        dict: {"request_data": str, "response_data": str}
    """
    try:
        response_dump = dump.dump_response(response, request_prefix="req:", response_prefix="res:").decode("utf-8", "ignore")
        req = re.sub("req:", "", '\n'.join(re.findall(r"(req:.*)", response_dump, re.MULTILINE)))
        res = re.sub("^res:", "", ''.join(re.search(r"(res:(.|\n)*)", response_dump, re.MULTILINE).groups()), flags=re.MULTILINE)[:-1]
        return {"request": req, "response": res}
    except Exception as e:
        return {"request": "error", "response": "error"}


def _get_response(url: str, method: str, headers: dict, proxies: dict, data: dict = None, timeout: int = None, redirects: bool = False, verify: bool = False, auth: tuple[str, str] = None, cookies: dict = {}) -> requests.Response:
    try:
        cookies = _get_cookies_from_headers(headers)
        response = requests.request(method, url, proxies=proxies, allow_redirects=redirects, headers=headers, verify=verify, timeout=timeout, data=data, auth=auth, cookies=cookies)
    except requests.exceptions.RequestException as error:
        raise error
    return response


def _get_cookies_from_headers(headers: dict) -> dict | None:
    if "Cookie" not in headers:
        return None

    cookies_object = SimpleCookie()
    cookies_object.load(headers["Cookie"])
    cookies = {key: morsel.value for key, morsel in cookies_object.items()}
    return cookies

def load_url(url: str, method: str, **kwargs) -> requests.Response:
    """
    A simplified version that delegates to the full function with fewer arguments.
    """
    return load_url_from_web_or_temp(url, method, **kwargs)

def load_url_from_web_or_temp(url: str, method: str, headers: dict = {}, proxies: dict = {}, data: dict = None, timeout: int = None, redirects: bool = False, verify: bool = False, cache: bool = False, dump_response: bool = False, auth: tuple[str, str] = None, cookies: dict = {}) -> requests.Response:
    """Returns HTTP response from URL.
       If param <cache_request> is present, response will be saved into a temp file. If response is already saved in a temp file, it will be loaded from there.

    Args:
        url            (str)  : request url
        method         (str)  : request method
        headers        (dict) : request headers
        proxies        (dict) : request proxies
        data           (dict) : request post data
        timeout        (int)  : request timeout
        redirects      (bool) : follow redirects
        verify         (bool) : verify requests
        cache          (bool) : cache request-response
        dump_response  (bool) : dump request-response
        auth           (tuple[str, str]) : use HTTP authentication
        cookies        (dict) : cookies

    Returns:
        default:
            requests.models.Response: response
        with dump_response:
            tuple: ( response: requests.Response, request_dump: dict )
    """
    if cache:
        # Create penterep dir in tmp if not present
        if not os.path.exists(get_penterep_temp_dir()):
            os.makedirs(get_penterep_temp_dir())

        filename = get_temp_filename_from_url(url, method, headers)
        if exists_temp(filename):
            obj = load_object(filename)
            return obj["response"] if not dump_response else (obj["response"], obj["response_dump"])
        else:
            response = _get_response(url, method, headers, proxies, data, timeout, redirects, verify, auth, cookies)
            response_dump = get_response_data_dump(response)
            save_object({"response": response, "response_dump": response_dump}, filename)
            return response if not dump_response else (response, response_dump)
    else:
        response = _get_response(url, method, headers, proxies, data, timeout, redirects, verify, auth, cookies)
        return response if not dump_response else (response, get_response_data_dump(response))

def read_temp_dir() -> tuple[int, int]:
    """
    Reads the 'pentereptools' temp directory.

    Returns:
        tuple: (item_count, total_size_bytes)
            - item_count: number of files and folders inside
            - total_size_bytes: total size of all files in bytes
    """
    temp_path = get_penterep_temp_dir()
    if not os.path.exists(temp_path):
        return 0, 0

    total_size = 0
    item_count = 0

    for root, dirs, files in os.walk(temp_path):
        item_count += len(dirs) + len(files)
        for file in files:
            file_path = os.path.join(root, file)
            try:
                total_size += os.path.getsize(file_path)
            except OSError:
                pass  # file might have been deleted during read

    return item_count, total_size

def clear_temp_dir() -> None:
    """
    Deletes all contents of the 'pentereptools' temp directory, but keeps the directory itself.
    """
    temp_path = get_penterep_temp_dir()
    if not os.path.exists(temp_path):
        os.makedirs(temp_path)
        return

    for entry in os.listdir(temp_path):
        entry_path = os.path.join(temp_path, entry)
        try:
            if os.path.isfile(entry_path) or os.path.islink(entry_path):
                os.unlink(entry_path)
            elif os.path.isdir(entry_path):
                shutil.rmtree(entry_path)
        except Exception as e:
            print(f"Warning: failed to delete {entry_path}: {e}")
    return True

def get_penterep_temp_dir() -> str:
    """Get folder for http request cache"""
    return os.path.join(os.path.expanduser("~"), ".penterep", f"http_cache")

def clean_html(input_html):
    """
    Removes all HTML tags from the input string, replacing <br>, <br/> and </p> tags with newlines.

    Parameters:
    input_html (str): A string containing HTML content.

    Returns:
    str: The cleaned string with no HTML tags and certain tags replaced by newline characters.
    """
    # Replace <br>, <br/>, and </p> tags with \n
    patterns_to_newline = re.compile(r'(<br\s*/?>|</p>)', re.IGNORECASE)
    text_with_newlines = re.sub(patterns_to_newline, '\n', input_html)

    # Remove all other HTML tags
    clean_text = re.sub(r'<.*?>', '', text_with_newlines)

    return clean_text.rstrip()

def get_tlds():
    """Returns a list of unique TLDs"""
    path_to_tld = os.path.join(os.path.dirname(__file__), 'data', 'iana_tlds.txt')
    tlds = {line.strip() for line in open(path_to_tld) if len(line.strip().split()) == 1}
    return tlds


