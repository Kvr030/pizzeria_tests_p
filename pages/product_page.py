from pages.base_page import BasePage


class ProductPage(BasePage):
    PRODUCT_TITLE = "h1.product_title"
    PRODUCT_PRICE = ".price"
    ADD_TO_CART_BUTTON = "button.single_add_to_cart_button"

    BOARD_SELECT = "select[name='board_pack']"
    BOARD_OPTION_CHEESE = "select[name='board_pack'] option[value='55.00']"
    BOARD_OPTION_SAUSAGE = "select[name='board_pack'] option[value='65.00']"
    BOARD_OPTION_REGULAR = "select[name='board_pack'] option[value='']"

    def __init__(self, page):
        super().__init__(page)

    def is_product_page_loaded(self) -> bool:
        return self.is_visible(self.PRODUCT_TITLE, "Заголовок товара")

    def get_product_title(self) -> str:
        return self.page.text_content(self.PRODUCT_TITLE)

    def add_to_cart(self):
        self.click(self.ADD_TO_CART_BUTTON, "Кнопка 'В корзину' на странице товара")

    def select_board_option(self, option_type: str = "cheese"):
        if option_type.lower() == "cheese":
            self.page.select_option(self.BOARD_SELECT, value="55.00")
            self.logger.info("Выбран сырный борт (+55₽)")
        elif option_type.lower() == "sausage":
            self.page.select_option(self.BOARD_SELECT, value="65.00")
            self.logger.info("Выбран колбасный борт (+65₽)")
        else:
            self.page.select_option(self.BOARD_SELECT, value="")
            self.logger.info("Выбран обычный борт")

        self.page.wait_for_timeout(500)

    def get_selected_board_option(self) -> str:
        selected_value = self.page.locator(self.BOARD_SELECT).input_value()
        if selected_value == "55.00":
            return "cheese"
        elif selected_value == "65.00":
            return "sausage"
        else:
            return "regular"

    def add_to_cart_with_board(self, board_type: str = "cheese"):
        self.select_board_option(board_type)
        self.add_to_cart()
