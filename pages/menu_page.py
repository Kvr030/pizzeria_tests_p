from pages.base_page import BasePage


class MenuPage(BasePage):
    MENU_LINK = "a[href*='product-category/menu']"
    DESSERTS_CATEGORY = "a[href*='deserts']"
    PRICE_FILTER_SLIDER = ".ui-slider"
    PRICE_SLIDER_HANDLE_MAX = ".ui-slider-handle:last-child"
    PRICE_FILTER_BUTTON = "button[type='submit']"
    PRICE_DISPLAY = ".price_slider_amount"
    PRODUCT_CARDS = ".product"
    PRODUCT_PRICE = ".price .amount"
    PRODUCT_TITLE = ".woocommerce-loop-product__title"

    def __init__(self, page):
        super().__init__(page)
        self.url = "https://pizzeria.skillbox.cc/product-category/menu/"

    def open(self):
        self.go_to(self.url)

    def click_menu_link(self):
        self.click(self.MENU_LINK, "Ссылка 'Меню'")

    def select_desserts_category(self):
        desserts_link = self.page.locator("a[href*='deserts']").first

        desserts_link.evaluate("element => element.click()")

        self.page.wait_for_timeout(3000)
        self.logger.info("Перешли в категорию 'Десерты'")

    def set_max_price(self, max_price: int):

        from_price = self.page.locator("span.from")
        to_price = self.page.locator("span.to")
        slider = self.page.locator(".ui-slider")

        current_min = int(from_price.text_content().replace("₽", "").strip())
        current_max = int(to_price.text_content().replace("₽", "").strip())

        self.logger.info(f"Текущий диапазон: {current_min}₽ - {current_max}₽")
        self.logger.info(f"Цель: {max_price}₽")

        price_range = current_max - current_min
        target_percentage = ((max_price - current_min) / price_range) * 100

        slider_handles = self.page.locator(".ui-slider-handle")
        right_handle = slider_handles.nth(1)

        slider_box = slider.bounding_box()

        target_x = slider_box["x"] + (slider_box["width"] * target_percentage / 100)
        target_y = slider_box["y"] + slider_box["height"] / 2

        right_handle.hover()
        self.page.wait_for_timeout(500)

        self.page.mouse.down()
        self.page.wait_for_timeout(300)

        self.page.mouse.move(target_x, target_y)
        self.page.wait_for_timeout(300)

        self.page.mouse.up()
        self.page.wait_for_timeout(1000)

        new_max = int(to_price.text_content().replace("₽", "").strip())
        self.logger.info(f"Новая максимальная цена: {new_max}₽")

        if abs(new_max - max_price) > 5:
            correction = ((max_price - new_max) / price_range) * 100
            self._adjust_slider(right_handle, slider_box, correction)

    def _adjust_slider(self, handle, slider_box, correction_percentage):
        target_x = slider_box["x"] + (slider_box["width"] * correction_percentage / 100)
        target_y = slider_box["y"] + slider_box["height"] / 2

        handle.hover()
        self.page.mouse.down()
        self.page.mouse.move(target_x, target_y)
        self.page.mouse.up()
        self.page.wait_for_timeout(500)

    def _drag_slider_with_mouse(self, slider_handle, slider_box, target_percentage):
        slider_handle.hover()

        self.page.mouse.down()

        target_x = slider_box["x"] + (slider_box["width"] * target_percentage / 100)
        target_y = slider_box["y"] + slider_box["height"] / 2

        self.page.mouse.move(target_x, target_y)

        self.page.mouse.up()

        self.logger.info(f"Перетащили ползунок к {target_percentage}%")

    def apply_filters(self):
        apply_button = self.page.locator("button:has-text('Применить')")
        apply_button.click()
        self.page.wait_for_timeout(2000)

    def get_visible_products_count(self) -> int:
        return self.page.locator(self.PRODUCT_CARDS).count()

    def get_product_prices(self) -> list:
        prices = []
        price_elements = self.page.locator(self.PRODUCT_PRICE)

        for i in range(price_elements.count()):
            price_text = price_elements.nth(i).text_content()
            import re

            amount_match = re.search(r"[\d,]+", price_text)
            if amount_match:
                price = float(amount_match.group().replace(",", "."))
                prices.append(price)

        return prices

    def get_product_titles(self) -> list:
        titles = []
        title_elements = self.page.locator(self.PRODUCT_TITLE)

        for i in range(title_elements.count()):
            title = title_elements.nth(i).text_content().strip()
            titles.append(title)

        return titles

    def are_all_prices_below_max(self, max_price: int) -> bool:
        prices = self.get_product_prices()
        if not prices:
            return False

        return all(price <= max_price for price in prices)

    def add_product_to_cart(self, product_index: int = 0):
        add_to_cart_buttons = self.page.locator("a.add_to_cart_button")
        add_button = add_to_cart_buttons.nth(product_index)

        add_button.scroll_into_view_if_needed()
        add_button.click()

        self.page.wait_for_timeout(2000)
        self.logger.info(f"Добавили товар #{product_index} в корзину")

    def get_cart_amount_from_header(self) -> float:
        cart_link = self.page.locator("a.cart-contents")
        if cart_link.is_visible():
            cart_text = cart_link.text_content()
            self.logger.info(
                f"Текст в корзине: '{cart_text}'"
            )  # Добавим лог для отладки

            import re

            amount_match = re.search(r"\[?\s*([\d,]+\.?[\d]*)\s*₽\s*\]?", cart_text)

            if amount_match:
                amount_str = amount_match.group(1).replace(",", "").replace(" ", "")
                try:
                    amount = float(amount_str)
                    self.logger.info(f"Распарсенная сумма: {amount}₽")
                    return amount
                except ValueError as e:
                    self.logger.error(f"Ошибка парсинга суммы '{amount_str}': {e}")

        self.logger.warning("Не удалось получить сумму из корзины")
        return 0.0
