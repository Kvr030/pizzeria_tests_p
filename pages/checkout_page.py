import datetime
from pages.base_page import BasePage


class CheckoutPage(BasePage):

    LOGIN_LINK = "a.showlogin"
    CHECKOUT_FORM = ".woocommerce-checkout"
    GUEST_CHECKOUT = "input#createaccount"
    LOGIN_FORM = ".woocommerce-form-login"
    FIRST_NAME_FIELD = "#billing_first_name"
    LAST_NAME_FIELD = "#billing_last_name"
    ADDRESS_FIELD = "#billing_address_1"
    CITY_FIELD = "#billing_city"
    POSTCODE_FIELD = "#billing_postcode"
    PHONE_FIELD = "#billing_phone"
    EMAIL_FIELD = "#billing_email"

    DELIVERY_DATE_FIELD = "#delivery_date"
    PAYMENT_METHOD_CASH = "input[name='payment_method'][value='cod']"
    TERMS_CHECKBOX = "#terms"
    PLACE_ORDER_BUTTON = "#place_order"

    def __init__(self, page):
        super().__init__(page)
        self.url = "https://pizzeria.skillbox.cc/checkout/"

    def open(self):
        self.go_to(self.url)

    def is_login_link_visible(self) -> bool:
        return self.is_visible(self.LOGIN_LINK, "Ссылка 'Авторизуйтесь'")

    def is_checkout_page_loaded(self) -> bool:
        return (
            self.page.is_visible(self.CHECKOUT_FORM)
            or self.page.is_visible("#customer_details")
            or "/checkout/" in self.page.url
        )

    def click_login_link(self):
        self.click(self.LOGIN_LINK, "Ссылка 'Авторизуйтесь'")
        self.page.wait_for_selector(self.LOGIN_FORM, state="visible", timeout=5000)

    def is_checkout_form_visible(self) -> bool:
        return self.page.is_visible("form.checkout") or self.page.is_visible(
            "#customer_details"
        )

    def get_prefilled_email(self) -> str:
        email_field = self.page.locator("#billing_email")
        if email_field.is_visible():
            return email_field.input_value()
        return ""

    def get_cart_total_amount(self) -> float:
        total_selectors = [
            ".order-total .amount",
            ".cart_totals .amount:last-child",
            "tr.order-total .amount",
            "td[data-title='Итого'] .amount",
        ]

        for selector in total_selectors:
            total_element = self.page.locator(selector)
            if total_element.is_visible():
                total_text = total_element.text_content()
                self.logger.info(f"Найден текст суммы: '{total_text}'")

                import re

                amount_match = re.search(r"[\d,]+", total_text)
                if amount_match:
                    amount = float(amount_match.group().replace(",", "."))
                    self.logger.info(f"Общая сумма заказа: {amount}₽")
                    return amount

        self.logger.error("Не удалось найти общую сумму заказа")
        return 0.0

    def fill_required_fields(self, user_data: dict):
        fields_to_fill = {
            "#billing_first_name": "ТестовоеИмя",
            "#billing_last_name": "ТестоваяФамилия",
            "#billing_address_1": "Тестовая улица, 123",
            "#billing_city": "Москва",
            "#billing_state": "Москва",
            "#billing_postcode": "123456",
            "#billing_phone": "+79991234567",
        }

        for selector, value in fields_to_fill.items():
            if self.page.is_visible(selector):
                self.fill(selector, value, f"Поле {selector}")

        email_field = self.page.locator("#billing_email")
        if email_field.is_visible() and not email_field.input_value():
            self.fill("#billing_email", user_data["email"], "Email")

    def fill_delivery_form(self):
        from utilities.test_data import test_data

        user_data = test_data.get_registered_user()

        if not user_data:
            user_data = {"email": "test@example.com"}

        self.fill_required_fields(user_data)

        region_selectors = [
            "#billing_state",
            "select[name='billing_state']",
            "#billing_region",
        ]
        for selector in region_selectors:
            if self.page.is_visible(selector):
                try:
                    self.page.select_option(selector, value="MOS")  # Москва
                    self.logger.info(" Выбран регион: Москва")
                    break
                except Exception:
                    self.page.fill(selector, "Москва")
                    self.logger.info(" Введен регион: Москва")
                    break

        self.logger.info(" Форма доставки полностью заполнена")

    def select_delivery_date_tomorrow(self):
        tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime(
            "%Y-%m-%d"
        )

        date_selectors = [
            "#delivery_date",
            "input[name='delivery_date']",
            "input[type='date']",
            ".delivery_date",
        ]

        for selector in date_selectors:
            date_field = self.page.locator(selector)
            if date_field.is_visible():
                date_field.fill(tomorrow)
                self.logger.info(f"✅ Выбрана дата доставки: {tomorrow}")
                return

        self.logger.warning(
            " Поле даты доставки не найдено, используем дату по умолчанию"
        )

    def select_cash_on_delivery(self):
        cash_radio = self.page.locator(self.PAYMENT_METHOD_CASH)
        if cash_radio.is_visible():
            cash_radio.click()
            self.logger.info("Выбрана оплата при доставке")
        else:
            payment_methods = self.page.locator(
                ".payment_methods input, .wc_payment_methods input"
            )
            if payment_methods.count() > 0:
                payment_methods.first.click()
                self.logger.info("Выбран первый доступный способ оплаты")

    def accept_terms(self):
        terms_checkbox = self.page.locator(self.TERMS_CHECKBOX)
        if terms_checkbox.is_visible():
            terms_checkbox.check()
            self.logger.info("Приняты условия соглашения")

    def place_order(self):
        self.click(self.PLACE_ORDER_BUTTON, "Кнопка 'Подтвердить заказ'")
        self.page.wait_for_timeout(5000)

    def is_order_received(self) -> bool:
        self.page.wait_for_timeout(5000)

        success_indicators = [
            "order-received" in self.page.url,
            "order-received" in self.page.url,
            "thank-you" in self.page.url,
            self.page.is_visible(".woocommerce-order-received"),
            self.page.is_visible(".order-received"),
            self.page.is_visible(".woocommerce-thankyou"),
            self.page.is_visible("h2:has-text('Заказ получен')"),
            self.page.is_visible(":has-text('Заказ подтвержден')"),
            self.page.is_visible(".order strong"),
            self.page.is_visible(".order-number"),
            self.page.is_visible("li.order"),
        ]

        current_url = self.page.url
        page_title = self.page.title()
        self.logger.info(f" Текущий URL: {current_url}")
        self.logger.info(f" Заголовок страницы: {page_title}")

        visible_elements = []
        for indicator in [
            ".woocommerce-order-received",
            ".order-received",
            ".woocommerce-thankyou",
            ".order",
        ]:
            if self.page.is_visible(indicator):
                visible_elements.append(indicator)

        self.logger.info(f" Видимые элементы подтверждения: {visible_elements}")

        return any(success_indicators)

    def apply_promocode(self, promocode: str):
        show_coupon_link = "a.showcoupon"
        coupon_field_selector = "#coupon_code"
        apply_coupon_selector = "button[name='apply_coupon']"

        coupon_field = self.page.locator(coupon_field_selector)

        if not coupon_field.is_visible():
            self.logger.info(
                "Поле для промокода скрыто. Нажимаю на ссылку для его раскрытия."
            )
            self.click(show_coupon_link, "Ссылка 'Нажмите для ввода купона'")

            try:
                coupon_field.wait_for(state="visible", timeout=5000)
                self.logger.info(" Поле для ввода промокода успешно раскрыто")
            except Exception as e:
                self.logger.error(
                    f"Не удалось дождаться появления поля для промокода: {e}"
                )
        else:
            self.logger.info("Поле для промокода уже видно.")

        self.fill(coupon_field_selector, promocode, "Поле для промокода")

        self.click(apply_coupon_selector, "Кнопка 'Применить купон'")

        self.page.wait_for_timeout(3000)

        self.logger.info(f" Попытка применения промокода: {promocode}")

    def get_cart_subtotal(self) -> float:
        subtotal_element = self.page.locator(".cart-subtotal .amount")
        if subtotal_element.is_visible():
            subtotal_text = subtotal_text = subtotal_element.text_content()
            import re

            amount_match = re.search(r"[\d,]+", subtotal_text)
            if amount_match:
                return float(amount_match.group().replace(",", ""))
        return 0.0

    def get_discount_amount(self) -> float:
        discount_element = self.page.locator(
            ".cart-discount .amount, .coupon-discount .amount"
        )
        if discount_element.is_visible():
            discount_text = discount_element.text_content()
            import re

            amount_match = re.search(r"[\d,]+", discount_text)
            if amount_match:
                return float(amount_match.group().replace(",", ""))
        return 0.0

    def is_promocode_applied(self, promocode: str = "") -> bool:
        self.page.wait_for_timeout(1000)

        success_indicators = [
            self.page.is_visible(".cart-discount"),
            self.page.is_visible(".coupon-applied"),
            self.page.is_visible(".woocommerce-message:has-text('успешно')"),
            self.page.is_visible(f".woocommerce-message:has-text('{promocode}')"),
            self._has_discount_been_applied(),
        ]

        if any(success_indicators):
            self.logger.info(" Обнаружены признаки успешного применения промокода")
            return True

        self.logger.info(" Признаки успешного применения промокода отсутствуют")
        return False

    def _has_discount_been_applied(self) -> bool:
        discount_element = self.page.locator(".cart-discount .amount")
        if discount_element.is_visible():
            discount_text = discount_element.text_content()
            return "-" in discount_text or "−" in discount_text
        return False

    def get_order_number(self) -> str:
        order_number_elem = self.page.locator(".order strong, .order-number")
        if order_number_elem.is_visible():
            return order_number_elem.text_content()
        return ""

    def get_order_total(self) -> str:
        total_selectors = [
            ".order-total .amount",
            ".woocommerce-order-overview__total .amount",
            ".order_details .total .amount",
            "td[data-title='Итого'] .amount",
            "th:has-text('Итого') + td .amount",
        ]

        for selector in total_selectors:
            total_elem = self.page.locator(selector)
            if total_elem.is_visible():
                total_text = total_elem.text_content().strip()
                if total_text:
                    self.logger.info(f" Найдена сумма заказа: {total_text}")
                    return total_text

        amount_elements = self.page.locator(".amount").all()
        for elem in amount_elements:
            text = elem.text_content().strip()
            if "₽" in text or "руб" in text.lower():
                self.logger.info(f" Найдена сумма по валюте: {text}")
                return text

        self.logger.error(" Не удалось найти сумму заказа")
        return ""

    def is_promocode_error(self, promocode: str = "") -> bool:
        error_indicators = [
            self.page.is_visible(".woocommerce-error"),
            self.page.is_visible(".woocommerce-notice:has-text('недействителен')"),
            self.page.is_visible(".woocommerce-notice:has-text('не найден')"),
            self.page.is_visible(f".woocommerce-error:has-text('{promocode}')"),
        ]

        if any(error_indicators):
            error_text = self.page.locator(".woocommerce-error").text_content()
            self.logger.info(f" Ошибка применения промокода: {error_text}")
            return True

        success_indicators = [
            self.page.is_visible(".cart-discount"),
            self.page.is_visible(".coupon-applied"),
            self.page.is_visible(".woocommerce-message:has-text('успешно')"),
        ]

        if any(success_indicators):
            self.logger.info(" Промокод применился, но не должен был")
            return False

        return False

    def is_server_error_displayed(self) -> bool:
        error_indicators = [
            self.page.is_visible(".woocommerce-error:has-text('сервер')"),
            self.page.is_visible(".woocommerce-error:has-text('ошибка 500')"),
            self.page.is_visible(".error:has-text('временно недоступен')"),
            self.page.is_visible(".woocommerce-notice:has-text('попробуйте позже')"),
        ]
        return any(error_indicators)
