from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.chrome import ChromeType
from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium_stealth import stealth


def load_driver(use_stealth: bool = False) -> webdriver.Chrome:

    chrome_service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())

    chrome_options = Options()
    options = [
        "--headless",
        "--window-size=1920,1200",
        "--disable-extensions",
        "--user-data-dir='Profile 3"
    ]

    for option in options:
        chrome_options.add_argument(option)

    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

    if use_stealth:
        stealth(
            driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win64",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )

    return driver

def manual_load_driver(driver_path: str, user_data_path: str = None, headless: bool = True, use_stealth: bool = True) -> webdriver.Chrome:

    chrome_service = Service(driver_path)

    chrome_options = Options()
    chrome_options.add_argument("start-maximized")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    
    if headless:
        chrome_options.add_argument("--headless")

    if user_data_path:
        chrome_options.add_argument(f"user-data-dir={user_data_path}")

    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

    if use_stealth:
        stealth(
            driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win64",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )

    return driver
