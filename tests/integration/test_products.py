import pytest
from qapck.misc import sleep_for
from qapck.handlers.open_cart import OpenCart

@pytest.mark.products
class TestProducts:
    """
    Test case group for the products catalog.
    """

    @pytest.fixture(scope="class", autouse=True)
    def setup_class(self, app_handler: OpenCart):
        """
        Setup the test class with the OpenCart application handler.
        """
        self.app_handler = app_handler

    @sleep_for(2.0)
    @pytest.mark.parametrize("query", ["apple", "samsung", "banana", ""])
    def test_name_filtering(self, app_handler: OpenCart, query: str, get_queries: dict):
        """
        Verify that filtering products works correctly.

        Args:
            app_handler (OpenCart): The OpenCart application handler.
            query (str): The search query.
            get_queries (dict): A dictionary with expected product counts for each query.
        """
        app_handler.filter_products(query)
        items = app_handler.get_products()

        assert len(items) == get_queries[query], f"Expected {get_queries[query]} products but found {len(items)}."
        assert all(query in item['Product Name'].lower() for item in items), "Not all products match the query."

    @sleep_for(2.0)
    @pytest.mark.parametrize("order", ["asc", "desc"])
    def test_sorting(self, app_handler: OpenCart, order: str):
        """
        Verify that the products can be sorted by price.

        Args:
            app_handler (OpenCart): The OpenCart application handler.
            order (str): Sort order (asc or desc).
        """
        app_handler.filter_products('MacBook')
        app_handler.sort_products(order)
        items = app_handler.get_products()
        page_url = app_handler.driver.current_url

        prices = [item['Price'].replace('$', '').replace(',', '') for item in items]
        prices = [float(price) for price in prices]

        if order == 'asc':
            expected = sorted(prices)
        else:
            expected = sorted(prices, reverse=True)

        assert 'sort' in page_url and 'price' in page_url, "URL does not contain sorting parameters."
        assert prices == expected, f"Products are not sorted by price in {order} order."

    @sleep_for(2.0)
    def test_product_details(self, app_handler: OpenCart, product_sample: dict):
        """
        Verify that the product details page is correct.

        Args:
            app_handler (OpenCart): The OpenCart application handler.
            product_sample (dict): A dictionary with product sample data for verification.
        """
        product = app_handler.get_product(product_sample['id'])
        sample_values = product_sample['values']

        for key, value in sample_values.items():
            if not isinstance(value, str):
                product[key] = float(product[key])

        assert all(product[key] == value for key, value in sample_values.items()), \
            "Product details do not match the expected values."
        
    def test_price_filtering(self, app_handler: OpenCart):
        """
        Verify that filtering products by price works correctly.

        Args:
            app_handler (OpenCart): The OpenCart application handler.
        """
        app_handler.filter_products(100.00, 'filter_price')
        items = app_handler.get_products()

        prices = []

        for item in items:
            price = item['Price'].replace('$', '').replace(',', '')
            price = price.split('\n')[0]
            prices.append(float(price))

        assert all(price == 100.00 for price in prices)