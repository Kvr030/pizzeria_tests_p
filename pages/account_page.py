from pages.base_page import BasePage
from utilities.test_data import test_data
import random
import string


class AccountPage(BasePage):
    LOGIN_LINK = "a.account"
    REGISTER_BUTTON = "button.custom-register-button"
    USERNAME_FIELD = "#reg_username"
    EMAIL_FIELD = "#reg_email"
    PASSWORD_FIELD = "#reg_password"
    SUBMIT_REGISTER_BUTTON = "button.woocommerce-form-register__submit"
    SUCCESS_MESSAGE = ".woocommerce-MyAccount-content"

    def __init__(self, page):
        super().__init__(page)
        self.url = "https://pizzeria.skillbox.cc/my-account/"

    def open(self):
        self.go_to(self.url)

    def click_login_link(self):
        self.click(self.LOGIN_LINK, "Ссылка 'Войти'")
        self.page.wait_for_timeout(2000)

    def click_register_button(self):
        register_btn = self.page.locator(self.REGISTER_BUTTON)
        register_btn.hover()
        self.page.wait_for_timeout(500)
        register_btn.click()
        self.page.wait_for_timeout(2000)

    def generate_random_credentials(self):
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

        username = f"user_{random_suffix}"[:19]
        email = f"t{random_suffix}@ex.com"[:19]
        password = "Pass123!"[:19]

        self.logger.info(
            f"Сгенерированы данные: user='{username}' ({len(username)}),"
            f" email='{email}' ({len(email)}), password='{password}' ({len(password)})")

        return username, email, password

    def fill_registration_form(self, username: str, email: str, password: str):
        self.fill(self.USERNAME_FIELD, username, "Имя пользователя")

        self.fill(self.EMAIL_FIELD, email, "Адрес почты")

        self.fill(self.PASSWORD_FIELD, password, "Пароль")

    def submit_registration(self):
        self.click(self.SUBMIT_REGISTER_BUTTON, "Кнопка 'Зарегистрироваться'")
        self.page.wait_for_timeout(3000)

    def is_registration_successful(self) -> bool:
        self.page.wait_for_timeout(3000)

        success_indicators = [
            "my-account" in self.page.url,

            self.page.is_visible(".woocommerce-MyAccount-content"),

            self.page.is_visible(".woocommerce-MyAccount-navigation"),

            self.page.is_visible("p:has-text('Привет')"),

            not self.page.is_visible(".woocommerce-error")
        ]

        current_url = self.page.url
        self.logger.info(f"Текущий URL: {current_url}")

        page_title = self.page.title()
        self.logger.info(f"Заголовок страницы: {page_title}")

        visible_elements = []
        selectors = [".woocommerce-MyAccount-content", ".woocommerce-MyAccount-navigation",
                     ".woocommerce-error", ".woocommerce-message", "p", "h1", "h2"]

        for selector in selectors:
            if self.page.is_visible(selector):
                element = self.page.locator(selector).first
                text = element.text_content()[:100]
                visible_elements.append(f"{selector}: {text}")

        self.logger.info(f"Видимые элементы: {visible_elements}")

        return any(success_indicators)

    def complete_registration(self):
        username, email, password = self.generate_random_credentials()

        self.logger.info(f"Начинаем регистрацию пользователя: {username}")

        self.fill_registration_form(username, email, password)
        self.submit_registration()

        test_data.save_registered_user(username, email, password)

        self.logger.info(f"Данные пользователя сохранены: {username}")

        return username, email, password

    def logout(self):
        if "my-account" in self.page.url:
            logout_link = self.page.locator(".woocommerce-MyAccount-navigation a[href*='customer-logout']")

            if logout_link.is_visible():
                logout_link.click()
                self.page.wait_for_timeout(3000)
                self.logger.info(" Вышли из аккаунта")
                return True
            else:
                self.logger.info(" Кнопка выхода не найдена")
        else:
            self.logger.info(" Не на странице аккаунта, выход не требуется")
        return False
