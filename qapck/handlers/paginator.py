from selenium.webdriver.remote.webelement import WebElement

class Paginator:

    def __init__(self, page_info: dict) -> None:
        

        self.total_items = page_info['total_items']
        self.total_pages = page_info['total_pages']
        self.first_item  = page_info['first_item']
        self.last_item   = page_info['last_item']

        self.first: WebElement = None
        self.prev:  WebElement = None
        self.next:  WebElement = None
        self.last:  WebElement = None