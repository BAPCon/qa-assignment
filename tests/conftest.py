from selenium.common.exceptions import NoSuchDriverException
from qapck.handlers.load import manual_load_driver
from qapck.handlers.open_cart import OpenCart
from qapck.misc import disable_logging
import pytest

def pytest_addoption(parser):
    parser.addoption("--driver", action="store", default=None, help="Path to the driver executable")
    parser.addoption("--profile", action="store", default=None, help="Path to the user data directory")

@pytest.fixture(scope="session")
def app_handler(request):
    # Get the driver and profile options
    driver  = request.config.getoption("--driver")
    driver = str(driver)

    try:
        # Initialize instance of `OpenCart`
        app_handler = OpenCart()
        app_handler.driver = manual_load_driver(driver)
    except NoSuchDriverException as e:
        pytest.exit(f"Driver not found: {e}")

    # Perform login
    app_handler.login()
    yield app_handler

    # Teardown
    app_handler.driver.quit()


@pytest.fixture(scope="session")
def get_queries():
    """
    Return a dict of queries and expected results.
    """
    return {
        "apple": 1,
        "samsung": 2,
        "banana": 0,
        "": 10
    }


@pytest.fixture(scope="function")
def product_sample():
    return {
        "id": 42,
        "values": {
            "name": "Apple Cinema 30\"",
            "price": 100.0,
            "quantity": 951.0,
            "model": "Product 15",
            "manufacturer": "Apple",
            "image": "catalog/demo/apple_cinema_30.jpg"
        }

    }
