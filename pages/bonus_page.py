from pages.base_page import BasePage
import random
import string


class BonusPage(BasePage):
    BONUS_LINK = "a[href*='bonus']"
    USERNAME_FIELD = "#bonus_username"
    PHONE_FIELD = "#bonus_phone"
    SUBMIT_BUTTON = "button[name='bonus']"
    SUCCESS_MESSAGE = "text=Ваша карта оформлена!"

    def __init__(self, page):
        super().__init__(page)
        self.url = "https://pizzeria.skillbox.cc/bonus/"

    def open(self):
        self.go_to(self.url)

    def open_from_header(self):
        bonus_link = self.page.locator(self.BONUS_LINK).first
        bonus_link.click()
        self.page.wait_for_timeout(2000)
        self.logger.info(" Перешли на страницу бонусной программы")

    def generate_random_name(self):
        names = [
            "Алексей",
            "Мария",
            "Иван",
            "Елена",
            "Дмитрий",
            "Ольга",
            "Сергей",
            "Анна",
        ]
        return random.choice(names)

    def generate_random_phone(self):
        first_digit = random.choice(["8", "7"])
        rest_numbers = "".join(random.choices(string.digits, k=10))
        phone = f"{first_digit}{rest_numbers}"
        return phone

    def fill_bonus_form(self, name: str = None, phone: str = None):
        if name is None:
            name = self.generate_random_name()
        if phone is None:
            phone = self.generate_random_phone()

        self.fill(self.USERNAME_FIELD, name, "Имя для бонусной карты")

        self.fill(self.PHONE_FIELD, phone, "Телефон для бонусной карты")

        self.logger.info(f" Заполнена форма бонусной программы: {name}, {phone}")
        return name, phone

    def submit_form(self):
        self.click(self.SUBMIT_BUTTON, "Кнопка 'Оформить карту'")
        self.page.wait_for_timeout(2000)
        self.logger.info(" Форма бонусной программы отправлена")

    def press_enter_to_confirm(self):
        self.page.keyboard.press("Enter")
        self.page.wait_for_timeout(1000)
        self.logger.info(" Нажата клавиша Enter для подтверждения")

    def is_success_message_displayed(self) -> bool:
        try:
            self.page.wait_for_selector(self.SUCCESS_MESSAGE, timeout=5000)
            success_text = self.page.locator(self.SUCCESS_MESSAGE).text_content()
            self.logger.info(f" Сообщение об успехе: {success_text}")
            return True
        except Exception:
            self.logger.warning(" Сообщение об успехе не отображено")
            return False

    def complete_bonus_registration(self):
        name, phone = self.fill_bonus_form()

        self.submit_form()

        self.press_enter_to_confirm()

        success = self.is_success_message_displayed()

        if success:
            self.logger.info(" Регистрация в бонусной программе завершена успешно!")
            return name, phone
        else:
            self.logger.error(" Регистрация в бонусной программе не удалась")
            return None, None
