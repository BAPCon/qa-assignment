from datetime import datetime
import json
import pytest
from qapck.misc import sleep_for
from qapck.handlers.open_cart import OpenCart

@pytest.mark.reports
class TestReports:
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
    def test_report_date_filtering(self, app_handler: OpenCart, date_range: tuple = ('2024-09-01', '2024-09-30',)):
        """
        Verify that reports can be filtered by date.

        Args:
            app_handler (OpenCart): The OpenCart application handler.
            date_range (tuple): The date range to filter the reports.
        """

        def get_report_dates(report: dict):
            rs = datetime.strptime(report['Date Start'], '%d/%m/%Y')
            re = datetime.strptime(report['Date End'], '%d/%m/%Y')
            return rs, re

        app_handler.filter_reports(filter_date_start=date_range[0], filter_date_end=date_range[1])
        items = app_handler.get_table()

        start_date = datetime.strptime(date_range[0], '%Y-%m-%d')
        end_date = datetime.strptime(date_range[1], '%Y-%m-%d')

        for item in items:
            rs, re = get_report_dates(item)
            assert start_date <= rs <= end_date
            assert start_date <= re <= end_date

    @sleep_for(2.0)
    @pytest.mark.parametrize("grouped_by", [("week", 7,), ("month", 30,)])
    def test_report_grouping(self, app_handler: OpenCart, grouped_by: tuple):
        """
        Verify that report grouping works as intended.
        Validates report dates are within the expected range.

        Args:
            app_handler (OpenCart): The OpenCart application handler.
        """

        print(grouped_by)

        def get_report_dates(report: dict):
            rs = datetime.strptime(report['Date Start'], '%d/%m/%Y')
            re = datetime.strptime(report['Date End'], '%d/%m/%Y')
            return rs, re
        
        app_handler.filter_reports(grouped_by=grouped_by[0])
        items = app_handler.get_table()

        for item in items:
            rs, re = get_report_dates(item)
            assert (re - rs).days <= grouped_by[1]