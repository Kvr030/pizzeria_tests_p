import pytest
import allure
from utilities.test_data import test_data
from utilities.logger import logger


@allure.title("Блок 2 - Сценарий 1: Успешное применение промокода GIVEMEHALYAVA")
def test_valid_promocode_applies_10_discount(page, menu_page, cart_page, checkout_page, account_page):
    logger.info(" Начало Сценария 1: Проверка валидного промокода")

    with allure.step("1. Авторизоваться зарегистрированным пользователем"):
        account_page.open()
        if "my-account" in page.url and page.is_visible("input#username"):
            user_data = test_data.get_registered_user()
            if user_data:
                page.fill("#username", user_data["email"])
                page.fill("#password", user_data["password"])
                page.click("button[name='login']")
                page.wait_for_timeout(3000)
                logger.info(f" Выполнен вход пользователя: {user_data['username']}")

    with allure.step("2. Проверить состояние корзины и очистить при необходимости"):
        cart_page.open()

        if not cart_page.is_cart_empty():
            logger.info(" В корзине есть товары - начинаем очистку")

            cart_page.remove_all_promocodes()

            items_count = cart_page.get_cart_items_count()
            for i in range(items_count):
                cart_page.remove_product(0)
                page.wait_for_timeout(1000)

            if cart_page.is_cart_empty():
                logger.info(" Корзина успешно очищена")
            else:
                logger.warning(" Корзина не полностью очищена")
        else:
            logger.info(" Корзина уже пуста - очистка не требуется")

    with allure.step("3. Добавить новый товар в корзину"):
        menu_page.open()
        menu_page.select_desserts_category()
        menu_page.add_product_to_cart(0)
        page.wait_for_timeout(2000)
        logger.info(" Товар добавлен в корзину")

    with allure.step("4. Перейти к оформлению заказа через хедер"):
        checkout_link = page.locator("a[href*='checkout']").first
        checkout_link.click()
        page.wait_for_timeout(2000)

        assert "/checkout/" in page.url, "Не удалось перейти на страницу оформления"
        logger.info(" Страница оформления заказа загружена")

        initial_total = checkout_page.get_cart_total_amount()
        logger.info(f" Сумма в корзине до промокода: {initial_total}₽")

    with allure.step("5. Проверить и удалить промокод если он уже применен"):
        applied_coupon = page.locator(".cart-discount, .coupon-applied").is_visible()
        if applied_coupon:
            logger.info(" Найден примененный промокод - удаляем")
            remove_btn = page.locator("a.woocommerce-remove-coupon")
            if remove_btn.is_visible():
                remove_btn.click()
                page.wait_for_timeout(2000)
                logger.info(" Промокод удален")

        total_before = checkout_page.get_cart_total_amount()
        logger.info(f" Итоговая сумма до применения промокода: {total_before}₽")
        assert total_before > 0, "Итоговая сумма должна быть больше 0"

    with allure.step("6. Применить промокод GIVEMEHALYAVA"):
        checkout_page.apply_promocode("GIVEMEHALYAVA")

    with allure.step("7. Проверить, что промокод применился успешно"):
        page.wait_for_timeout(3000)

        success_indicators = [
            page.is_visible(".woocommerce-message:has-text('GIVEMEHALYAVA')"),
            page.is_visible(".woocommerce-message:has-text('успешно')"),
            page.is_visible(".cart-discount"),
            page.is_visible(".coupon-applied")
        ]

        assert any(success_indicators), "Промокод не применился - нет признаков успеха"
        logger.info(" Промокод успешно применен")

    with allure.step("8. Проверить, что сумма заказа уменьшилась на 10%"):
        total_after = checkout_page.get_cart_total_amount()
        logger.info(f" Итоговая сумма после промокода: {total_after}₽")

        expected_total = total_before * 0.9

        difference = abs(total_after - expected_total)
        assert difference < 1, (
            f"Скидка 10% не применена корректно. Было: {total_before}₽, Стало: {total_after}₽, "
            f"Ожидалось: {expected_total:.2f}₽, Разница: {difference:.2f}₽"
        )

        actual_discount = ((total_before - total_after) / total_before) * 100
        logger.info(f" Скидка {actual_discount:.1f}% применена корректно. Итоговая сумма: {total_after}₽")

    logger.info(" Сценарий 1 завершен успешно! Промокод работает корректно.")


@allure.title("Блок 2 - Сценарий 2: Невалидный промокод DC120 не применяется")
def test_invalid_promocode_does_not_apply_discount(page, menu_page, cart_page, checkout_page):
    logger.info(" Начало Сценария 2: Проверка невалидного промокода DC120")

    with allure.step("2. Подготовить чистую корзину"):
        cart_page.open()

        if not cart_page.is_cart_empty():
            cart_page.remove_all_promocodes()
            items_count = cart_page.get_cart_items_count()
            for i in range(items_count):
                cart_page.remove_product(0)
                page.wait_for_timeout(1000)

        assert cart_page.is_cart_empty(), "Корзина должна быть пустой перед началом теста"

    with allure.step("3. Добавить новый товар в корзину"):
        menu_page.open()
        menu_page.select_desserts_category()
        menu_page.add_product_to_cart(0)
        page.wait_for_timeout(2000)
        logger.info(" Товар добавлен в корзину")

    with allure.step("4. Перейти к оформлению заказа через хедер"):
        checkout_link = page.locator("a[href*='checkout']").first
        checkout_link.click()
        page.wait_for_timeout(2000)

        assert "/checkout/" in page.url, "Не удалось перейти на страницу оформления"
        logger.info(" Страница оформления заказа загружена")

        initial_total = checkout_page.get_cart_total_amount()
        logger.info(f" Сумма в корзине до промокода: {initial_total}₽")

    with allure.step("5. Запомнить исходную сумму до применения промокода"):
        total_before = checkout_page.get_cart_total_amount()
        logger.info(f" Итоговая сумма до промокода: {total_before}₽")
        assert total_before > 0, "Итоговая сумма должна быть больше 0"

    with allure.step("6. Применить невалидный промокод DC120"):
        checkout_page.apply_promocode("DC120")
        page.wait_for_timeout(3000)

    with allure.step("7. Проверить, что промокод НЕ применился"):
        assert checkout_page.is_promocode_error("DC120"), "Должна быть ошибка применения промокода"
        logger.info(" Промокод DC120 правильно не применился - ошибка отображена")

        success_applied = checkout_page.is_promocode_applied("DC120")
        assert not success_applied, "Промокод DC120 не должен применяться успешно"
        logger.info(" Нет признаков успешного применения промокода")

    with allure.step("8. Проверить, что сумма заказа НЕ изменилась"):
        total_after = checkout_page.get_cart_total_amount()
        logger.info(f" Итоговая сумма после попытки применения: {total_after}₽")

        assert abs(total_after - total_before) < 0.01, (
            f"Сумма не должна изменяться. Было: {total_before}₽, Стало: {total_after}₽"
        )
        logger.info(" Сумма заказа не изменилась - промокод не сработал")

    with allure.step("9. Проверить отсутствие скидки в деталях заказа"):
        discount_block = page.locator(".cart-discount, .coupon-discount")
        assert not discount_block.is_visible(), "Не должно быть блока скидки"
        logger.info(" Блок скидки отсутствует")

    logger.info(" Сценарий 2 завершен успешно! Невалидный промокод правильно отклонен.")


@allure.title("Блок 2 - Сценарий 3: Сервер промокодов недоступен")
def test_promocode_server_error_handling(page, menu_page, cart_page, checkout_page):
    logger.info(" Начало Сценария 3: Проверка обработки ошибки сервера промокодов")

    with allure.step("1. Подготовить чистую корзину"):
        cart_page.open()

        if not cart_page.is_cart_empty():
            cart_page.remove_all_promocodes()
            items_count = cart_page.get_cart_items_count()
            for i in range(items_count):
                cart_page.remove_product(0)
                page.wait_for_timeout(1000)

        assert cart_page.is_cart_empty(), "Корзина должна быть пустой"

    with allure.step("2. Добавить новый товар в корзину"):
        menu_page.open()
        menu_page.select_desserts_category()
        menu_page.add_product_to_cart(0)
        page.wait_for_timeout(2000)
        logger.info(" Товар добавлен в корзину")

    with allure.step("3. Перейти к оформлению заказа через хедер"):

        checkout_link = page.locator("a[href*='checkout']").first
        checkout_link.click()
        page.wait_for_timeout(2000)

        assert "/checkout/" in page.url, "Не удалось перейти на страницу оформления"
        logger.info(" Страница оформления заказа загружена")

        initial_total = checkout_page.get_cart_total_amount()
        logger.info(f" Сумма в корзине до промокода: {initial_total}₽")

    with allure.step("4. Запомнить исходную сумму"):
        total_before = checkout_page.get_cart_total_amount()
        logger.info(f" Сумма до промокода: {total_before}₽")

    with allure.step("5. Перехватить запросы к серверу промокодов"):
        intercepted_requests = []

        def abort_request(route):
            intercepted_requests.append(route.request.url)
            logger.info(f" Блокируем запрос: {route.request.url}")
            route.abort()

        page.route("**/wp-admin/admin-ajax.php*", abort_request)
        page.route("**/admin-ajax.php*", abort_request)
        page.route("**/*coupon*", abort_request)

        logger.info(" Перехват запросов активирован")

    with allure.step("6. Применить промокод при заблокированном сервере"):
        checkout_page.apply_promocode("GIVEMEHALYAVA")
        page.wait_for_timeout(5000)

    with allure.step("7. Диагностика: что произошло после применения"):
        logger.info(" ДИАГНОСТИКА СОСТОЯНИЯ СТРАНИЦЫ:")

        elements_to_check = {
            "Сообщение об ошибке": ".woocommerce-error",
            "Сообщение об успехе": ".woocommerce-message",
            "Блок скидки": ".cart-discount",
            "Примененный купон": ".coupon-applied"
        }

        for name, selector in elements_to_check.items():
            if page.is_visible(selector):
                text = page.locator(selector).text_content()
                logger.info(f"   {name}: ВИДИМ - '{text}'")
            else:
                logger.info(f"   {name}: не виден")

    with allure.step("8. Проверить сумму заказа (главный критерий)"):
        total_after = checkout_page.get_cart_total_amount()
        logger.info(f" Сумма после попытки применения: {total_after}₽")

        amount_unchanged = abs(total_after - total_before) < 0.01

        if amount_unchanged:
            logger.info(" Сумма не изменилась - промокод не сработал")
        else:
            logger.error(f" Сумма ИЗМЕНИЛАСЬ! Было: {total_before}₽, Стало: {total_after}₽")
            page.screenshot(path="screenshots/server_error_bug.png")
            logger.info(" Скриншот сохранен: screenshots/server_error_bug.png")

    with allure.step("9. Проверить наличие ошибки сервера"):
        if amount_unchanged:
            logger.info(" ТЕСТ ПРОЙДЕН: Система корректно обработала ошибку сервера")
        else:
            success_applied = checkout_page.is_promocode_applied("GIVEMEHALYAVA")

            if success_applied and not amount_unchanged:
                logger.error(" ВОЗМОЖНЫЙ БАГ: Промокод применился несмотря на ошибку сервера!")
            else:
                logger.warning("️ Неоднозначный результат - требуется дополнительный анализ")

    with allure.step("10. Отключить перехват запросов"):
        page.unroute("**/wp-admin/admin-ajax.php*")
        page.unroute("**/admin-ajax.php*")
        page.unroute("**/*coupon*")

    assert abs(total_after - total_before) < 0.01, (
        f"БАГ: Промокод применился при ошибке сервера! Было: {total_before}₽, Стало: {total_after}₽"
    )


@allure.title("Блок 2 - Сценарий 4: Проверка однократности применения промокода")
def test_promocode_one_time_use_only(page, menu_page, checkout_page):
    logger.info(" Начало Сценария 4: Проверка однократности промокода")

    with allure.step("1. Выход из аккаунта и регистрация нового пользователя"):
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
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        username = f"user_{random_suffix}"[:19]
        email = f"t{random_suffix}@ex.com"[:19]
        password = "Pass123!"[:19]

        page.fill("#reg_username", username)
        page.fill("#reg_email", email)
        page.fill("#reg_password", password)
        page.click("button.woocommerce-form-register__submit")
        page.wait_for_timeout(3000)

        if page.is_visible(".woocommerce-error"):
            error_text = page.locator(".woocommerce-error").text_content()
            pytest.fail(f"Ошибка регистрации: {error_text}")

        logger.info(f" Пользователь зарегистрирован: {username}")

    with allure.step("2. Первый заказ с применением промокода"):
        menu_page.open()
        menu_page.select_desserts_category()
        menu_page.add_product_to_cart(0)
        page.wait_for_timeout(1000)

        checkout_link = page.locator("a[href*='checkout']").first
        checkout_link.click()
        page.wait_for_timeout(2000)

        first_order_original_amount = checkout_page.get_cart_total_amount()
        logger.info(f" Сумма первого заказа: {first_order_original_amount}₽")

        checkout_page.apply_promocode("GIVEMEHALYAVA")
        page.wait_for_timeout(2000)

        amount_with_discount = checkout_page.get_cart_total_amount()
        discount = first_order_original_amount - amount_with_discount
        logger.info(f" Скидка для первого заказа: {discount:.2f}₽")

        checkout_page.fill_delivery_form()
        checkout_page.select_delivery_date_tomorrow()
        checkout_page.select_cash_on_delivery()
        checkout_page.accept_terms()
        checkout_page.place_order()
        page.wait_for_timeout(4000)

        assert checkout_page.is_order_received(), "Первый заказ не оформлен"
        first_order_number = checkout_page.get_order_number()
        first_order_final_amount = checkout_page.get_order_total()
        logger.info(f" Первый заказ оформлен! Номер: {first_order_number}, Сумма: {first_order_final_amount}")

    with allure.step("3. Второй заказ с попыткой применения того же промокода"):
        menu_page.open()
        menu_page.select_desserts_category()
        menu_page.add_product_to_cart(0)
        page.wait_for_timeout(1000)

        checkout_link = page.locator("a[href*='checkout']").first
        checkout_link.click()
        page.wait_for_timeout(2000)

        second_order_original_amount = checkout_page.get_cart_total_amount()
        logger.info(f" Сумма второго заказа: {second_order_original_amount}₽")

        checkout_page.apply_promocode("GIVEMEHALYAVA")
        page.wait_for_timeout(2000)

        checkout_page.fill_delivery_form()
        checkout_page.select_delivery_date_tomorrow()
        checkout_page.select_cash_on_delivery()
        checkout_page.accept_terms()
        checkout_page.place_order()
        page.wait_for_timeout(4000)

        assert checkout_page.is_order_received(), "Второй заказ не оформлен"
        second_order_number = checkout_page.get_order_number()
        second_order_final_amount = checkout_page.get_order_total()
        logger.info(f" Второй заказ оформлен! Номер: {second_order_number}")

    with allure.step("4. Проверка суммы второго заказа после оформления"):
        logger.info(f" Итоговая сумма второго заказа: {second_order_final_amount}")

        def parse_amount(amount_text):
            if isinstance(amount_text, (int, float)):
                return float(amount_text)
            cleaned = str(amount_text).replace('₽', '').replace(' ', '').replace(',', '.')
            return float(cleaned)

        original_amount = parse_amount(second_order_original_amount)
        final_amount = parse_amount(second_order_final_amount)

        logger.info(" Сравнение сумм:")
        logger.info(f"   Ожидаемая сумма (без скидки): {original_amount}₽")
        logger.info(f"   Фактическая сумма: {final_amount}₽")
        logger.info(f"   Разница: {abs(final_amount - original_amount):.2f}₽")

        amount_difference = abs(final_amount - original_amount)

        if amount_difference > 1:
            unauthorized_discount = original_amount - final_amount
            pytest.fail(f"БАГ: Промокод применился повторно! "
                        f"Второй заказ получил скидку {unauthorized_discount:.2f}₽")
        else:
            logger.info(" Промокод не применился повторно - тест пройден")

    logger.info(" Сценарий 4 завершен успешно! Промокод работает только один раз.")
