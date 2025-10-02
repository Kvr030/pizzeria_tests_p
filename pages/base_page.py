from playwright.sync_api import Page
from utilities.logger import logger


class BasePage:
    def __init__(self, page: Page):
        self.page = page
        self.logger = logger

    def go_to(self, url: str):
        self.logger.info(f"Перехожу по адресу: {url}")
        self.page.goto(url)

    def click(self, locator: str, element_name: str = "Элемент"):
        self.logger.info(f"Кликаю на '{element_name}' (локатор: {locator})")
        self.page.click(locator)

    def fill(self, locator: str, text: str, element_name: str = "Поле ввода"):
        self.logger.info(
            f"Ввожу текст '{text}' в '{element_name}' (локатор: {locator})"
        )
        self.page.fill(locator, text)

    def is_visible(self, locator: str, element_name: str = "Элемент") -> bool:
        is_visible = self.page.is_visible(locator)
        log_message = f"Элемент '{element_name}' виден: {is_visible}"
        if is_visible:
            self.logger.info(log_message)
        else:
            self.logger.warning(log_message)
        return is_visible

    def logout(self):
        if "my-account" in self.page.url:
            pass
