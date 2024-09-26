from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from seleniumwire import webdriver
from typing import List, Dict, Tuple
from typing import Dict, Tuple

class DashboardTile:
    """
    A helper class to represent and extract details from a dashboard tile element.
    """

    @staticmethod
    def get_dashboard_tiles(driver: webdriver.Chrome) -> List[Dict[str, str]]:
        """
        Fetches the tiles present on the dashboard page.

        :return: A list of dictionary items representing dashboard tiles.
        :rtype: List[Dict[str, str]]
        """
        xpath = "//div[contains(@class, 'tile tile-primary')]"
        tile_elements = driver.find_elements(By.XPATH, xpath)
        return [DashboardTile.extract(element) for element in tile_elements]
    

    @staticmethod
    def extract(element: WebElement) -> Dict[str, str]:
        """
        Extracts details from a dashboard tile element.

        :param element: The WebElement of the dashboard tile.
        :type element: WebElement
        :return: Extracted details from the tile.
        :rtype: Dict[str, str]
        """
        title, float_end = DashboardTile._get_title_and_float_end(element)
        body_value = DashboardTile._get_body_value(element)
        link = DashboardTile._get_footer_link(element)

        return {
            "title": title,
            "value": body_value,
            "link": link,
            "float_end": float_end,
        }

    @staticmethod
    def _get_title_and_float_end(element: WebElement) -> Tuple[str, str]:
        """
        Extracts the title and float_end from a tile element.

        :param element: The WebElement of the tile.
        :type element: WebElement
        :return: The title and float_end text.
        :rtype: Tuple[str, str]
        """
        heading_element = element.find_element(
            By.XPATH, ".//div[contains(@class, 'tile-heading')]")
        try:
            float_end = heading_element.find_element(
                By.XPATH, ".//span[contains(@class, 'float-end')]").text
        except Exception:
            float_end = "0%"

        title = heading_element.text.replace(float_end, "").strip()
        return title, float_end

    @staticmethod
    def _get_body_value(element: WebElement) -> float:
        """
        Extracts the body value from a tile element.

        :param element: The WebElement of the tile.
        :type element: WebElement
        :return: The body value.
        :rtype: float
        """
        body_value_text = element.find_element(
            By.XPATH, ".//div[contains(@class, 'tile-body')]").text
        thousands = body_value_text.lower().endswith("k")
        value = float(body_value_text[:-1]
                      ) if thousands else float(body_value_text)
        return value * 1000 if thousands else value

    @staticmethod
    def _get_footer_link(element: WebElement) -> str:
        """
        Extracts the footer link from a tile element.

        :param element: The WebElement of the tile.
        :type element: WebElement
        :return: The URL of the footer link.
        :rtype: str
        """
        footer = element.find_element(
            By.XPATH, ".//div[contains(@class, 'tile-footer')]")
        return footer.find_element(By.TAG_NAME, "a").get_attribute("href")