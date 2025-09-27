from pages.base_page import BasePage


class MainPage(BasePage):
    SLIDER_CARDS = ".slick-slide:not(.slick-cloned)"

    ADD_TO_CART_BUTTON = "a.add_to_cart_button"

    CART_COUNTER = "a.cart-contents"

    PIZZA_IMAGE = "img.attachment-shop_catalog"

    SLIDER_NEXT_BUTTON = "a.slick-next"
    SLIDER_PREV_BUTTON = "a.slick-prev"

    SLIDER_AREA = ".slick-slide:not(.slick-cloned)"

    PRODUCT_TITLE_IN_CARD = "h3"

    def __init__(self, page):
        super().__init__(page)
        self.url = "https://pizzeria.skillbox.cc/"

    def open(self):
        self.go_to("/")

    def is_slider_visible(self) -> bool:
        return self.is_visible(self.SLIDER_CARDS, "Слайдер с товарами")

    def hover_first_pizza(self):
        self.logger.info("Навожу курсор на первую пиццу в слайдере")
        self.page.hover(self.SLIDER_CARDS + " >> nth=0")

    def hover_and_add_to_cart(self):
        self.logger.info("Навожу на первую пиццу и добавляю в корзину")

        pizza_card = self.page.locator(self.SLIDER_CARDS).first

        pizza_card.hover()

        self.page.wait_for_selector(self.ADD_TO_CART_BUTTON, state="visible", timeout=10000)

        add_button = pizza_card.locator(self.ADD_TO_CART_BUTTON)
        add_button.click()

        self.logger.info("Товар успешно добавлен в корзину")

    def get_cart_amount(self) -> float:
        self.page.wait_for_selector(self.CART_COUNTER, state="visible", timeout=5000)

        cart_text = self.page.text_content(self.CART_COUNTER)
        self.logger.info(f"Текст в корзине: '{cart_text}'")

        if cart_text:
            import re
            amount_match = re.search(r'[\d,]+\.?[\d]*(?=₽)|[\d,]+', cart_text)
            if amount_match:
                amount_str = amount_match.group().replace(',', '.').replace(' ', '')
                try:
                    amount = float(amount_str)
                    self.logger.info(f"Текущая сумма в корзине: {amount}₽")
                    return amount
                except ValueError:
                    pass

        self.logger.info("Корзина пуста или не удалось распарсить сумму")
        return 0.0


    def navigate_slider_and_verify(self, direction='next'):
        initial_slide = self.page.locator(".slick-slide.slick-active").first

        if direction == 'next':
            self.click_next_slider()
        else:
            self.click_prev_slider()

        self.page.wait_for_timeout(1000)

        new_slide = self.page.locator(".slick-slide.slick-active").first
        return initial_slide != new_slide

    def click_next_slider(self):
        prod_section = self.page.locator(".prod1-slider").first
        prod_section.hover()

        self.page.wait_for_selector(self.SLIDER_NEXT_BUTTON, state="visible", timeout=10000)

        self.click(self.SLIDER_NEXT_BUTTON, "Стрелка 'Вправо' слайдера")

    def click_prev_slider(self):
        prod_section = self.page.locator(".prod1-slider").first
        prod_section.hover()

        self.page.wait_for_selector(self.SLIDER_PREV_BUTTON, state="visible", timeout=10000)

        self.click(self.SLIDER_PREV_BUTTON, "Стрелка 'Влево' слайдера")

    def _hover_with_js(self, element_locator):
        self.page.evaluate("""
            (element) => {
                element.dispatchEvent(new MouseEvent('mouseover', { bubbles: true }));
                element.dispatchEvent(new MouseEvent('mousemove', { bubbles: true }));
            }
        """, element_locator.element_handle())
        self.page.wait_for_timeout(500)

    def click_first_pizza_image(self):
        self.click(self.PIZZA_IMAGE + " >> nth=0", "Изображение первой пиццы")

    def navigate_to_slide(self, slide_index: int):
        prod_section = self.page.locator(".prod1-slider").first
        prod_section.hover()

        for i in range(slide_index):
            self.page.wait_for_selector(self.SLIDER_NEXT_BUTTON, state="visible", timeout=5000)
            self.click(self.SLIDER_NEXT_BUTTON, f"Стрелка 'Вправо' для перехода к слайду {i + 1}")
            self.page.wait_for_timeout(500)  # Ждем анимацию

    def add_pizza_from_current_slide(self):
        active_card = self.page.locator(".slick-slide.slick-active").first

        active_card.hover()

        add_button = active_card.locator(self.ADD_TO_CART_BUTTON)
        add_button.wait_for(state="visible")
        add_button.click()

        self.logger.info("Добавили пиццу из текущего слайда в корзину")

    def click_current_active_product(self):
        active_card = self.page.locator(".slick-slide.slick-active").first

        active_card.scroll_into_view_if_needed()
        self.page.wait_for_timeout(500)

        active_card.hover()
        self.page.wait_for_timeout(500)

        product_title = active_card.locator("h3").first
        product_title.click()

        self.logger.info("Кликнул на товар в активной позиции слайдера")

    def click_product_by_visible_index(self, index: int = 0):
        visible_cards = self.page.locator(f"{self.SLIDER_CARDS}:visible")

        card_to_click = visible_cards.nth(index)
        card_to_click.scroll_into_view_if_needed()
        card_to_click.click()

        self.logger.info(f"Кликнул на товар с видимым индексом {index}")

    def go_to_cart(self):
        self.click(self.CART_COUNTER, "Ссылка на корзину в шапке")
        self.logger.info("Переход в корзину")
