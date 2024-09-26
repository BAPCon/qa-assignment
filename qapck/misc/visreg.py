from selenium.webdriver.remote.webelement import WebElement
from typing import Generator, Callable, List
from datetime import datetime, timedelta
from PIL import ImageChops, Image
from functools import wraps
from io import BytesIO
import time

def element_screenshot(element: WebElement) -> Image:
    """
    Takes a screenshot of a given web element and returns it as a PIL Image.

    Args:
        element (WebElement): The web element to take a screenshot of.

    Returns:
        Image: A PIL Image of the web element screenshot.
    """
    png = element.screenshot_as_png
    return Image.open(BytesIO(png))

def calculate_image_diff(im1: Image, im2: Image) -> float:
    """
    Calculates the pixel difference between two images.

    Args:
        im1 (Image): The first image.
        im2 (Image): The second image.

    Returns:
        float: The average pixel difference normalized to the range 0-1.
    """
    diff = ImageChops.difference(im1, im2)
    px_avg = average_image_pixels(diff)
    return px_avg / 255

def visual_generator(element: WebElement) -> Generator[Image.Image, None, None]:
    """
    A generator to yield screenshots of a web element.

    Args:
        element (WebElement): The web element to capture.

    Yields:
        Image: A PIL Image of the web element screenshot.
    """
    yield element_screenshot(element)
    yield element_screenshot(element)

def visual_regression(func: Callable):
    """
    A decorator to measure visual changes in a web element before and after a function call.

    Args:
        func (Callable): The function to wrap.

    Returns:
        Callable: The wrapped function.
    """
    @wraps(func)
    def wrapper(element: WebElement, *args, **kwargs) -> float:
        visreg = visual_generator(element)
        pre_image = next(visreg)
        result = func(element, *args, **kwargs)  # Execute the wrapped function
        post_image = next(visreg)
        return calculate_image_diff(pre_image, post_image)
    return wrapper

def average_image_pixels(im: Image.Image) -> float:
    """
    Averages the pixel values of an image.

    Args:
        im (Image): The image to process.

    Returns:
        float: The average pixel value.
    """
    px_arr = im.tobytes()
    px_arr = [int(px) for px in px_arr]
    return sum(px_arr) / len(px_arr)

def wait_for_element_to_settle(element: WebElement, check_interval: float = 0.1, timeout: float = 2.0, history_length: int = 3) -> bool:
    """
    Waits for the given element to visually settle.

    Args:
        element (WebElement): The web element to monitor.
        check_interval (float): Time in seconds to wait between each check.
        timeout (float): Maximum time in seconds to wait for the element to settle.
        history_length (int): Number of recent pixel averages to keep in history to determine settle.

    Returns:
        bool: True if the element settled within the timeout, False otherwise.
    """
    def get_average_pixel_value(element: WebElement) -> float:
        im = element_screenshot(element)
        return average_image_pixels(im)

    history: List[float] = []
    start_time = datetime.now()

    while datetime.now() - start_time < timedelta(seconds=timeout):
        current_pixel_value = get_average_pixel_value(element)
        history.append(current_pixel_value)

        if len(history) > history_length:
            history.pop(0)

        # Check if all the values in history are equal
        if len(set(history)) == 1 and len(history) == history_length:
            return True

        time.sleep(check_interval)

    return False