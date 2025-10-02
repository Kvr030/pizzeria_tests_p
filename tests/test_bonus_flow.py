import pytest
import allure
from utilities.logger import logger


@allure.title("Блок 3: Регистрация в бонусной программе")
def test_bonus_program_registration(page, account_page, bonus_page):

    logger.info("Начало теста: Регистрация в бонусной программе")

    with allure.step("1. Зарегистрировать нового пользователя"):
        page.goto("https://pizzeria.skillbox.cc/")
        page.wait_for_timeout(1000)

        logout_link = page.locator("a.logout").first
        if logout_link.is_visible():
            logout_link.click()
            page.wait_for_timeout(2000)

        page.goto("https://pizzeria.skillbox.cc/my-account/")
        page.wait_for_timeout(1000)

        register_btn = page.locator("button.custom-register-button")
        register_btn.hover()
        page.wait_for_timeout(500)
        register_btn.click()
        page.wait_for_timeout(1000)

        import random
        import string

        random_suffix = "".join(
            random.choices(string.ascii_lowercase + string.digits, k=6)
        )
        username = f"bonus_{random_suffix}"[:19]
        email = f"bonus{random_suffix}@test.com"[:19]
        password = "TestPass123!"[:19]

        page.fill("#reg_username", username)
        page.fill("#reg_email", email)
        page.fill("#reg_password", password)
        page.click("button.woocommerce-form-register__submit")
        page.wait_for_timeout(3000)

        if page.is_visible(".woocommerce-error"):
            error_text = page.locator(".woocommerce-error").text_content()
            pytest.fail(f"Ошибка регистрации: {error_text}")

        logger.info(f"Пользователь зарегистрирован: {username}")

    with allure.step("2. Перейти на страницу бонусной программы через хедер"):
        bonus_page.open_from_header()
        assert (
            "/bonus/" in page.url
        ), "Не удалось перейти на страницу бонусной программы"

    with allure.step("3. Заполнить форму бонусной программы"):
        assert page.is_visible(bonus_page.USERNAME_FIELD), "Поле имени не найдено"
        assert page.is_visible(bonus_page.PHONE_FIELD), "Поле телефона не найдено"

        name, phone = bonus_page.fill_bonus_form()
        logger.info(f"Заполнены данные: {name}, {phone}")

    with allure.step("4. Отправить форму и подтвердить"):
        bonus_page.submit_form()
        bonus_page.press_enter_to_confirm()
        page.wait_for_timeout(3000)

    with allure.step("5. Проверить успешность оформления бонусной карты"):
        success = bonus_page.is_success_message_displayed()
        assert success, "Сообщение об успешном оформлении карты не отображено"

        logger.info("Бонусная карта успешно оформлена!")

    with allure.step("6. Дополнительная проверка: валидация полей"):
        logger.info(
            " Основная проверка пройдена, валидация полей может быть добавлена отдельно"
        )

    logger.info("Тест бонусной программы завершен успешно!")
