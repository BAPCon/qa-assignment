<hr/>

# Usage

You can run the tests locally, though due to CloudFlare, I would suggest passing in a chrome user profile.

Command to run the tests:
```ps1
pytest -sv --driver="/path/to/driver" --profile="/path/to/profile/directory/"
```

If the DevTools logging bothers you, passing the flag `-dl` to disable logging.

<hr/>

# Test Results

```js
======================================================================================================= test session starts =======================================================================================================
platform win32 -- Python 3.12.0, pytest-8.3.3, pluggy-1.5.0 -- c:\Users\bperk\qa-rhombus\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\bperk\qa-rhombus
configfile: pytest.ini
testpaths: tests
collected 18 items

tests/integration/test_dashboard.py::TestDashboard::test_graph_ranges[month] PASSED
tests/integration/test_dashboard.py::TestDashboard::test_graph_ranges[week] PASSED
tests/integration/test_dashboard.py::TestDashboard::test_graph_ranges[day] SKIPPED

tests/integration/test_dashboard.py::TestDashboard::test_dashboard_tiles PASSED
tests/integration/test_dashboard.py::TestDashboard::test_latest_orders PASSED
tests/integration/test_dashboard.py::TestDashboard::test_order_counts PASSED
tests/integration/test_dashboard.py::TestDashboard::test_customer_counts PASSED

tests/integration/test_products.py::TestProducts::test_filtering[apple] PASSED
tests/integration/test_products.py::TestProducts::test_filtering[samsung] PASSED
tests/integration/test_products.py::TestProducts::test_filtering[banana] PASSED
tests/integration/test_products.py::TestProducts::test_filtering[] PASSED
tests/integration/test_products.py::TestProducts::test_sorting[asc] PASSED
tests/integration/test_products.py::TestProducts::test_sorting[desc] PASSED
tests/integration/test_products.py::TestProducts::test_product_details PASSED

tests/integration/test_reports.py::TestReports::test_report_grouping[grouped_by0] PASSED
tests/integration/test_reports.py::TestReports::test_report_grouping[grouped_by1] PASSED

============================================================================================ 17 passed, 1 skipped in 65.84s (0:01:05) =============================================================================================
```
<hr/>

# Test Case Descriptions
Plaintext description of the tests and their purpose.

## Dashboard Tests

### Test Case: `test_graph_ranges`
**Description:** Verifies whether changing the date filter (`month`, `week`, `day`) on the sales graph updates the graph data accordingly.

**Reason:** Ensures the functionality and data accuracy of the sales graph for different date ranges.

---

### Test Case: `test_dashboard_tiles`
**Description:** Ensures that the dashboard tiles contain expected keys (`title`, `value`, `link`) and correct number of tiles are displayed. Verifies that the tile values are numeric and their links are correct.

**Reason:** Validates the integrity and completeness of crucial dashboard statistics.

---

### Test Case: `test_latest_orders`
**Description:** Verifies that the latest orders are displayed correctly on the dashboard. Confirms that required keys (`Order ID`, `Date Added`, `Total`) appear on each order invoice.

**Reason:** Ensures the correctness of displayed order information and consistency with expected data format.

---

### Test Case: `test_order_counts`
**Description:** Validates that the order counts displayed on the dashboard tiles match the order counts on the orders page.

**Reason:** Ensures data consistency between the dashboard summary and detailed order data.

---

### Test Case: `test_customer_counts`
**Description:** Verifies that customer counts on the dashboard tiles match the counts on the customers page, allowing for a discrepancy ratio up to 10%.

**Reason:** Ensures accuracy and reliability of customer data overviews.

---

## Products Catalog Tests

### Test Case: `test_name_filtering`
**Description:** Verifies that product searching by specifying queries (`apple`, `samsung`, `banana`, `null`) works correctly and matches the expected product counts for each query.

**Reason:** Ensures search functionality works correctly with different keywords and expected results are accurate.

---

### Test Case: `test_sorting`
**Description:** Verifies that products can be sorted by price in ascending (`asc`) or descending (`desc`) order.

**Reason:** Confirms the correct implementation of sorting functionalities for product prices.

---

### Test Case: `test_product_details`
**Description:** Ensures that the product details page displays accurate information corresponding to sample data.

**Reason:** Validates the correctness of displayed product attributes on the details page.

---

### Test Case: `test_price_filtering`
**Description:** Confirms that filtering products based on price displays products only with the specified price.

**Reason:** Ensures the accuracy of price-based product filtering.

---

## Reports Tests

### Test Case: `test_report_date_filtering`
**Description:** Verifies that report filtering based on a specific date range (e.g. `'2024-09-01'` to `'2024-09-30'`) works correctly, ensuring report dates are within the specified range.

**Reason:** Ensures the correctness of date-based filtering for reports.

---

### Test Case: `test_report_grouping`
**Description:** Validates that grouping reports by time intervals (`week`, `month`) works correctly, ensuring report dates fall within expected grouped ranges.

**Reason:** Confirms the proper grouping functionality of reports by specified intervals.