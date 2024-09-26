from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from .load import load_driver, manual_load_driver
from typing import List, Dict

from ..misc import (
    resp_json,
    await_string_in_url,
    cloudflare
)


class OpenCart:
    """
    A class to represent the OpenCart functionalities.
    """

    def __init__(self):
        self.driver = None
        self.user_token: str = None
        self.max_seconds: int = 10

    def get(self, url: str) -> None:
        """
        Navigate the driver to a given URL and handle cloudflare.

        Args:
            - url (str): The URL to navigate to.
        """
        self.driver.get(url)
        cloudflare(self)

    def build_url(self, path: str) -> str:
        """
        Build a full URL with a given path and user token.

        Args:
            - path (str): The path to append to the base URL.

        Returns:
            - str: The complete URL.
        """
        return f'https://demo.opencart.com/admin/index.php?route={path}&user_token={self.user_token}'

    def get_orders_chart(self, element_key: str = 'month') -> Dict[str, List[Dict[str, float]]]:
        """
        Retrieve and parse order chart data.

        Args:
            - element_key (str): The key of the element to select in the chart range dropdown.

        Returns:
            - Dict[str, List[Dict[str, float]]]: Parsed data from the orders chart.
        """
        
        href = lambda e: e.get_attribute("href").split("/")[-1]
        options = self.driver.find_element(By.ID, "range")
        links = options.find_elements(By.TAG_NAME, "a")

        # Click the dropdown selector
        dropdown_selector = options.find_element(By.XPATH, "preceding-sibling::a")
        dropdown_selector.click()

        # Click the target element
        target = {href(e): e for e in links}[element_key]
        target.click()

        # Wait for the chart to update
        chart_request = self.driver.wait_for_request(f"range={element_key}", timeout=15)
        data = resp_json(chart_request)
        num_items = len(data["xaxis"])

        values = [(data["xaxis"][i][-1], data["customer"]["data"][i][-1]) for i in range(num_items)]
        return {"data": values, "range_key": chart_request.params["range"]}
    
    def get_invoice(self, order: dict = {}) -> dict:
        """
        Retrieve the invoice for the given order.

        Args:
            - order (dict): The order information.

        Returns:
            - dict: The invoice text.
        """
        self.invoice(order['Order ID'])
        condition = EC.presence_of_element_located((By.TAG_NAME, "body"))
        return WebDriverWait(self.driver, 10).until(condition).text
    
    def login(self) -> None:
        """
        Log into the OpenCart demo site and sets the user token.
        """
        self.get("https://demo.opencart.com/admin/")
        login_button = self.driver.find_element(By.TAG_NAME, "button")
        login_button.click()

        current_request = self.driver.wait_for_request("common/dashboard")
        self.user_token = current_request.params["user_token"]

    def dashboard(self) -> None:
        """
        Open the dashboard page.
        """
        self.get(self.build_url("common/dashboard"))
        await_string_in_url(self.driver, "common/dashboard")

    def orders(self) -> None:
        """
        Open the orders page.
        """
        self.get(self.build_url("sale/order.list"))
        await_string_in_url(self.driver, "sale/order")

    def customers(self) -> None:
        """
        Open the customers page.
        """
        self.get(self.build_url("customer/customer"))
        await_string_in_url(self.driver, "customer/customer")

    def invoice(self, order_id: str) -> None:
        """
        Open the invoice page for the given order.

        Args:
            - order_id (str): The ID of the order.
        """
        self.get(self.build_url(f"sale/order.invoice&order_id={order_id}"))
        await_string_in_url(self.driver, f"order_id={order_id}")

    def filter_products(self, query: str, filter_key: str = 'filter_name') -> None:
        """
        Open the products catalog with the specified query and filter key.

        Args:
            - query (str): The search query.
            - filter_key (str): The filter key to use.
        """
        self.get(self.build_url(f"catalog/product.list&{filter_key}={query}"))
        await_string_in_url(self.driver, f"{filter_key}={query}")

    def sort_products(self, order: str) -> None:
        """
        Sort the products by price.

        Args:
            - order (str): The order to sort the products.
        """
        sort_btn = self.driver.find_element(By.LINK_TEXT, "Price")
        while sort_btn.get_attribute('class') != order:
            sort_btn.click()
            sort_btn = self.driver.find_element(By.LINK_TEXT, "Price")

    def get_products(self) -> List[Dict[str, str]]:
        """
        Retrieve the products from the catalog.

        Returns:
            - List[Dict[str, str]]: The list of products.
        """
        return self.get_table()

    def get_product(self, product_id: int) -> dict:
        """
        Retrieve the attributes of a product.

        Args:
            - product_id (int): The product ID.

        Returns:
            - dict: The product attributes.
        """
        path = f"catalog/product.form&product_id={product_id}"
        base_url = self.build_url(path)

        self.get(base_url)
        await_string_in_url(self.driver, f"product_id={product_id}")

        attributes = {}

        image = self.driver.find_elements(By.CSS_SELECTOR, "input[type='hidden'][name='image']")
        attributes['image'] = image[0].get_attribute("value")

        for input in self.driver.find_elements(By.CSS_SELECTOR, "input[type='text']"):
            name  = input.get_attribute("name")
            value = input.get_attribute("value")
            if '[' in name:
                name = name.split('[')[-1].split(']')[0]
            if len(value) > len(attributes.get(name, '')):
                attributes[name] = value

        return attributes
    
    def filter_reports(self, filter_date_start: str = None, filter_date_end: str = None, grouped_by: str = 'month', category_path: str = 'extension/opencart/report/customer.list') -> None:
        """
        Open the reports page with specified filters.

        Args:
            - filter_date_start (str): The start date for the filter.
            - filter_date_end (str): The end date for the filter.
            - grouped_by (str): The grouping criterion.
            - category_path (str): The category path to filter on.
        """
        url = f"{category_path}"

        if filter_date_start:
            url += f"&filter_date_start={filter_date_start}"
        if filter_date_end:
            url += f"&filter_date_end={filter_date_end}"
        if grouped_by:
            url += f"&filter_group={grouped_by}"

        self.get(self.build_url(url))
        await_string_in_url(self.driver, category_path)

    def get_table(self, table: WebElement = None) -> dict:
        """
        Retrieve the items from the table on the current page.

        Returns:
            - dict: The items from the table and table name.
        """
        items = []
        table = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )

        rows = table.find_elements(By.TAG_NAME, "tr")
        headers = rows[0].find_elements(By.TAG_NAME, "td")
        headers = [header.text for header in headers]

        for row in rows[1:]:
            item = {}
            cells = [td for td in row.find_elements(By.TAG_NAME, "td")]
            for header, value in zip(headers, cells):
                if header.strip() and value.text.strip():
                    item[header] = value.text
            if item: items.append(item)
            
        return items