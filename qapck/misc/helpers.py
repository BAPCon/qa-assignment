import time
import json
import brotli
import re
import logging
from functools import wraps
from typing import Any, Generator, Union
from calendar import monthrange
from datetime import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from seleniumwire.request import Request
from seleniumwire import webdriver
from qapck.handlers.paginator import Paginator

__all__ = [
    'timed_await',
    'await_url',
    'await_string_in_url',
    'resp_json',
    'get_days_in_month',
    'get_expected_axis_length',
    'is_number',
    'parse_pagination_string',
    'disable_logging',
    'cloudflare',
    'get_pagination',
    'sleep_for'
]

def timed_await(max_seconds: int):
    """
    Decorator to limit the time a function can run for.

    Args:
        max_seconds (int): The maximum duration the function is allowed to run.

    Raises:
        TimeoutError: If the function runs for longer than max_seconds.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = datetime.now()
            for result in func(*args, **kwargs):
                if (datetime.now() - start_time).total_seconds() > max_seconds:
                    raise TimeoutError(f"Timed out after {max_seconds} seconds")
                if result:
                    return result
        return wrapper
    return decorator

@timed_await(max_seconds=30)
def await_url(driver: webdriver.Chrome, url: str, equal_to: bool = True) -> Generator[bool, None, None]:
    """
    Waits until the current URL matches or does not match the given URL.

    Args:
        driver (webdriver.Chrome): The Selenium WebDriver instance.
        url (str): The URL to wait for.
        equal_to (bool): Indicates whether to wait for the URL to match or not match.

    Yields:
        bool: True if the URL matches the given condition.
    """
    while True:
        yield (driver.current_url == url) == equal_to

@timed_await(max_seconds=30)
def await_string_in_url(driver: webdriver.Chrome, string: str) -> Generator[bool, None, None]:
    """
    Waits until the given string is present in the current URL.

    Args:
        driver (webdriver.Chrome): The Selenium WebDriver instance.
        string (str): The string to wait for in the URL.

    Yields:
        bool: True if the string is found in the current URL.
    """
    while True:
        yield string in driver.current_url

def resp_json(request: Request) -> Union[dict, list]:
    """
    Extracts the JSON data from a request.

    Args:
        request (Request): The SeleniumWire Request object.

    Returns:
        Union[dict, list]: The JSON data from the request.
    """
    encoding = request.response.headers.get('Content-Encoding', [])
    if 'br' in encoding:
        data = brotli.decompress(request.response.body).decode('utf-8')
    else:
        data = request.response.body.decode('utf-8')
    return json.loads(data)

def get_days_in_month(month: int = None, year: int = None) -> int:
    """
    Get the number of days in the given month, or the current month if not provided.

    Args:
        month (int, optional): The month number.
        year (int, optional): The year number.

    Returns:
        int: The number of days in the month.
    """
    now = datetime.now()
    month = month or now.month
    year = year or now.year
    return monthrange(year, month)[1]

def get_expected_axis_length(range_key: str) -> int:
    """
    Get the expected number of points for the range_key.

    Args:
        range_key (str): The range key, e.g., 'day', 'week', 'month', 'year'.

    Returns:
        int: The number of expected points.
    """
    if range_key == 'day':
        return 24
    elif range_key == 'week':
        return 7
    elif range_key == 'month':
        return get_days_in_month()
    elif range_key == 'year':
        return 12

def is_number(value: Any) -> bool:
    """
    Check if the given value is a number.

    Args:
        value (Any): The value to check.

    Returns:
        bool: True if the value is a number, otherwise False.
    """
    return isinstance(value, (int, float))

def parse_pagination_string(pagination_str: str) -> dict:
    """
    Parse the pagination string and return the total items, total pages, first item index, and last item index.

    Args:
        pagination_str (str): The pagination string to parse.

    Returns:
        dict: A dictionary containing pagination details.
    """
    pattern = r'Showing (\d+) to (\d+) of (\d+) \((\d+) Pages\)'
    match = re.match(pattern, pagination_str)
    if match:
        return {
            "total_items": int(match.group(3)),
            "total_pages": int(match.group(4)),
            "first_item": int(match.group(1)),
            "last_item": int(match.group(2))
        }
    else:
        raise ValueError("Invalid pagination string format")

def disable_logging():
    """
    Disable logging for all loggers related to Selenium.
    """
    handlers = logging.root.manager.loggerDict
    handlers = [n for n in handlers if 'selenium' in n]
    for handler in handlers:
        logging.getLogger(handler).setLevel(logging.ERROR)

def cloudflare(open_cart):
    """
    Bypass Cloudflare security checks.

    Args:
        open_cart (OpenCart): The OpenCart application handler.
    """
    cf_string = 'Just a moment'
    in_title = lambda driver: cf_string in open_cart.driver.title
    in_body = lambda driver: 'Verifying you are human' in open_cart.driver.page_source
    _cloudflare = lambda driver: in_title(driver) or in_body(driver)
    try:
        WebDriverWait(open_cart.driver, 15).until_not(_cloudflare)
    except Exception as e:
        logging.error(f"Error bypassing Cloudflare: {e}")

def get_pagination(driver: webdriver.Chrome) -> Paginator:
    """
    Get the pagination elements from the page.

    Args:
        driver (webdriver.Chrome): The Selenium WebDriver instance.

    Returns:
        Paginator: A Paginator object containing pagination details.
    """
    btn_list = driver.find_element(By.XPATH, '//ul[contains(@class, "pagination")]')
    u_parent = btn_list.find_element(By.XPATH, '..')
    next_div = u_parent.find_element(By.XPATH, 'following-sibling::div')
    pagination = Paginator(parse_pagination_string(next_div.text))

    btns = btn_list.find_elements(By.TAG_NAME, 'li')

    for btn in btns:
        if btn.text == '|<':
            pagination.first = btn
        elif btn.text == '<':
            pagination.prev = btn
        elif btn.text == '>|':
            pagination.last = btn
        elif btn.text == '>':
            pagination.next = btn

    return pagination

def sleep_for(seconds: float = 2.0):
    """
    Decorator that sleeps for a given amount of time before running the function.

    Args:
        seconds (float): The number of seconds to sleep.

    Returns:
        Callable: The wrapped function.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            time.sleep(seconds)
            return func(*args, **kwargs)
        return wrapper
    return decorator