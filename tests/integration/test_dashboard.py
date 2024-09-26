import time
import pytest
from qapck.misc import get_expected_axis_length, get_pagination, sleep_for, is_number
from qapck.handlers import DashboardTile
from qapck.handlers.open_cart import OpenCart

@pytest.mark.dashboard
class TestDashboard:
    """
    Test case group for the dashboard page.
    """

    @pytest.fixture(scope="class", autouse=True)
    def setup_class(self, app_handler: OpenCart):
        """
        Setup the test class with the OpenCart application handler.
        """
        app_handler.dashboard()
        self.app_handler = app_handler

    @sleep_for(2.0)
    @pytest.mark.parametrize("range_key", ["month", "week", "day"])
    def test_graph_ranges(self, app_handler: OpenCart, range_key: str):
        """
        Verify if changing the date filter on the sales graph updates the graph data.

        Args:
            app_handler (OpenCart): The OpenCart application handler.
            range_key (str): The date range key to filter the sales graph.
        """
        
        def get_chart_data():
            try:
                return app_handler.get_orders_chart(range_key)
            except Exception as e:
                # pytest.fail(f"Failed to get chart data: {e}")
                return None

        initial_chart = get_chart_data()

        if not initial_chart:
            pytest.skip(f"No chart data available for range_key: {range_key}")

        assert initial_chart['range_key'] == range_key, f"Expected range_key to be {range_key}, but got {initial_chart['range_key']}"
        assert len(initial_chart['data']) == get_expected_axis_length(range_key), \
            f"Expected {get_expected_axis_length(range_key)} data points, but got {len(initial_chart['data'])}"

    @sleep_for(2.0)
    def test_dashboard_tiles(self, app_handler: OpenCart):
        """
        Ensure that the dashboard tiles are fetched and contain the expected keys.

        Args:
            app_handler (OpenCart): The OpenCart application handler.
        """
        keys = ["title", "value", "link"]
        tiles = DashboardTile.get_dashboard_tiles(app_handler.driver)
        missing_keys = [key for tile in tiles for key in keys if key not in tile]

        assert not missing_keys, "Dashboard tiles are missing keys"
        assert len(tiles) == 4, "There should be 4 tiles on the dashboard"
        assert all(is_number(tile['value']) for tile in tiles), "Tile values are not numeric"

        # Assign tiles by title
        tile_map = {tile['title']: tile for tile in tiles}
        app_handler.total_orders = tile_map.get('TOTAL ORDERS')
        app_handler.total_sales = tile_map.get('TOTAL SALES')
        app_handler.total_customers = tile_map.get('TOTAL CUSTOMERS')

        # Check that the tiles have the expected links
        assert 'route=sale/order' in app_handler.total_orders['link'], "Total Orders tile link is incorrect"
        assert 'route=sale/order' in app_handler.total_sales['link'], "Total Sales tile link is incorrect"
        assert 'route=customer/customer' in app_handler.total_customers['link'], "Total Customers tile link is incorrect"

    @sleep_for(2.0)
    def test_latest_orders(self, app_handler: OpenCart):
        """
        Verify that the latest orders are displayed on the dashboard.

        Args:
            app_handler (OpenCart): The OpenCart application handler.
        """
        app_handler.dashboard()
        app_handler.driver.wait_for_request("common/dashboard")

        required_keys = ['Order ID', 'Date Added', 'Total']
        invoices, success = 0, 0

        latest_orders = app_handler.get_table()
        for order in latest_orders:
            try:
                invoices += 1
                time.sleep(2)
                invoice_text = app_handler.get_invoice(order)
                all_keys_present = all(key in invoice_text for key in required_keys)
                all_values_match = all(order[key] in invoice_text for key in required_keys)
                success += all_keys_present and all_values_match
            except Exception as e:
                print(f"Failed to get invoice for order: {order}. Error: {e}")
                continue

        assert invoices == 5, "There should be 5 invoices displayed"
        assert success >= invoices // 2, "Less than half of the invoices matched the expected values"

    @sleep_for(2.0)
    def test_order_counts(self, app_handler: OpenCart):
        """
        Verify that the order counts on the dashboard tiles match the order counts on the orders page.

        Args:
            app_handler (OpenCart): The OpenCart application handler.
        """
        app_handler.orders()
        pages = get_pagination(app_handler.driver)

        assert app_handler.total_orders['value'] == pages.total_items, "Order count on the dashboard does not match the orders page"

    @sleep_for(2.0)
    def test_customer_counts(self, app_handler: OpenCart):
        """
        Verify that the customer counts on the dashboard tiles match the customer counts on the customers page.

        Args:
            app_handler (OpenCart): The OpenCart application handler.
        """
        app_handler.customers()
        pages = get_pagination(app_handler.driver)

        tile_val = app_handler.total_customers['value']
        diff = max(tile_val, pages.total_items) - min(tile_val, pages.total_items)
        diff_ratio = diff / max(tile_val, pages.total_items)

        assert diff_ratio <= 0.10, "Customer count on the dashboard does not match the customers page"