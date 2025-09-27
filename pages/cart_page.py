from pages.base_page import BasePage


class CartPage(BasePage):
    CART_ITEMS_TABLE = ".shop_table.cart"
    CART_ITEM_ROW = "tr.cart_item"
    PRODUCT_NAME = ".product-name a"
    PRODUCT_PRICE = ".product-price"
    PRODUCT_QUANTITY = ".product-quantity input"
    PRODUCT_SUBTOTAL = ".product-subtotal"
    CART_TOTAL = ".cart_totals"
    UPDATE_CART_BUTTON = "button[name='update_cart']"
    REMOVE_ITEM_BUTTON = ".product-remove a"

    def __init__(self, page):
        super().__init__(page)
        self.url = "https://pizzeria.skillbox.cc/cart/"

    def open(self):
        self.go_to(self.url)

    def get_cart_items_count(self) -> int:
        return self.page.locator(self.CART_ITEM_ROW).count()

    def get_product_names(self) -> list:
        names = []
        items = self.page.locator(self.PRODUCT_NAME)
        for i in range(items.count()):
            names.append(items.nth(i).text_content().strip())
        return names

    def get_product_quantities(self) -> list:
        quantities = []
        items = self.page.locator(self.PRODUCT_QUANTITY)
        for i in range(items.count()):
            value = items.nth(i).get_attribute("value")
            quantities.append(int(value) if value else 1)
        return quantities

    def get_cart_total_amount(self) -> float:
        total_text = self.page.locator(".order-total .amount").last.text_content()
        import re
        amount_match = re.search(r'[\d,]+', total_text)
        if amount_match:
            return float(amount_match.group().replace(',', '.'))
        return 0.0

    def is_cart_empty(self) -> bool:
        return self.page.is_visible(".cart-empty")

    def update_product_quantity(self, product_index: int = 0, new_quantity: int = 2):
        quantity_field = self.page.locator(self.PRODUCT_QUANTITY).nth(product_index)

        quantity_field.fill("")
        quantity_field.fill(str(new_quantity))

        self.logger.info(f"Изменили количество товара #{product_index} на {new_quantity}")

    def click_update_cart(self):
        self.click(self.UPDATE_CART_BUTTON, "Кнопка 'Обновить корзину'")

        self.page.wait_for_timeout(3000)

        self.logger.info("Корзина обновлена")

    def get_product_quantity(self, product_index: int = 0) -> int:
        quantity_field = self.page.locator(self.PRODUCT_QUANTITY).nth(product_index)
        value = quantity_field.get_attribute("value")
        return int(value) if value else 1

    def get_product_subtotal(self, product_index: int = 0) -> float:
        subtotal_element = self.page.locator(f"{self.PRODUCT_SUBTOTAL} .amount").nth(product_index)
        subtotal_text = subtotal_element.text_content()

        self.logger.info(f"Текст суммы за товар #{product_index}: '{subtotal_text}'")

        import re
        amount_match = re.search(r'[\d,]+', subtotal_text)
        if amount_match:
            amount = float(amount_match.group().replace(',', '.'))
            self.logger.info(f"Распарсенная сумма: {amount}₽")
            return amount

        self.logger.warning(f"Не удалось распарсить сумму из текста: '{subtotal_text}'")
        return 0.0

    def remove_product(self, product_index: int = 0):
        initial_count = self.get_cart_items_count()

        remove_button = self.page.locator(self.REMOVE_ITEM_BUTTON).nth(product_index)
        remove_button.click()

        self.page.wait_for_function(
            f"document.querySelectorAll('{self.CART_ITEM_ROW}').length < {initial_count}",
            timeout=5000
        )

        self.page.wait_for_timeout(1000)

        self.logger.info(f"Удалили товар #{product_index} из корзины")

    def is_product_removed(self, product_index: int = 0) -> bool:
        try:
            current_count = self.get_cart_items_count()
            return current_count < (product_index + 1)
        except Exception:
            return False

    def get_remaining_product_names(self) -> list:
        return self.get_product_names()

    def proceed_to_checkout(self):
        self.click("a.checkout-button", "Кнопка 'Перейти к оплате'")
        self.page.wait_for_timeout(3000)
        self.logger.info("Перешли к оформлению заказа")

    def clear_cart(self):
        self.open()

        self.remove_all_promocodes()

        if self.is_cart_empty():
            self.logger.info("Корзина уже пуста")
            return

        items_count = self.get_cart_items_count()
        self.logger.info(f"Начинаем очистку корзины. Товаров: {items_count}")

        for i in range(items_count):
            self.remove_product(0)
            self.page.wait_for_timeout(1000)

        if self.is_cart_empty():
            self.logger.info(" Корзина успешно очищена")
        else:
            self.logger.warning(" Корзина не полностью очищена")

    def remove_all_promocodes(self):
        remove_buttons = self.page.locator("a.woocommerce-remove-coupon")

        removed_count = 0
        for i in range(remove_buttons.count()):
            remove_buttons.nth(i).click()
            self.page.wait_for_timeout(1000)
            removed_count += 1

        if removed_count > 0:
            self.logger.info(f" Удалено промокодов: {removed_count}")
        else:
            self.logger.info(" Нет примененных промокодов для удаления")

        return removed_count
