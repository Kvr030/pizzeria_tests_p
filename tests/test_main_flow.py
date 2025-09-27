import pytest
import allure
from pages.main_page import MainPage
from utilities.logger import logger
from utilities.test_data import test_data


@allure.title("TC-01: Отображение элементов главной страницы")
@pytest.mark.order(1)
def test_main_page_loads_successfully(page, main_page):
    logger.info("ТЕСТ 1: Начало выполнения")
    main_page = MainPage(page)

    with allure.step("Перейти на главную страницу"):
        main_page.open()

    with allure.step("Проверить видимость слайдера с товарами"):
        assert main_page.is_slider_visible(), "Слайдер с товарами не отображается на странице!"


@allure.title("TC-02: Добавление товара в корзину с главной страницы")
@pytest.mark.order(2)
def test_add_pizza_to_cart_from_main_page(page, main_page):
    logger.info("ТЕСТ 2: Начало выполнения")

    with allure.step("Запомнить начальную сумму в корзине"):
        initial_amount = main_page.get_cart_amount()
        main_page.logger.info(f"Начальная сумма: {initial_amount}₽")

    with allure.step("Навести на первую пиццу и нажать 'В корзину'"):
        main_page.hover_and_add_to_cart()

    with allure.step("Проверить что сумма в корзине увеличилась"):
        page.wait_for_timeout(1000)

        new_amount = main_page.get_cart_amount()
        main_page.logger.info(f"Новая сумма: {new_amount}₽")

        assert new_amount > initial_amount, (f"Сумма не увеличилась! "
                                             f"Было: {initial_amount}₽, Стало: {new_amount}₽")


@allure.title("TC-03: Навигация по слайдеру на главной странице")
@pytest.mark.order(3)
def test_slider_navigation(page, main_page):
    logger.info("ТЕСТ 3: Начало выполнения")

    with allure.step("Прокрутить слайдер вправо"):
        main_page.click_next_slider()

    with allure.step("Прокрутить слайдер влево"):
        main_page.click_prev_slider()

    with allure.step("Проверить что слайдер работает"):
        assert main_page.is_slider_visible(), "Слайдер не отображается после навигации!"


@allure.title("TC-04: Добавление товара в корзину после навигации по слайдеру")
@pytest.mark.order(4)
def test_add_pizza_after_slider_navigation(page, main_page):
    logger.info("ТЕСТ 4: Начало выполнения")

    with allure.step("Запомнить текущую сумму в корзине"):
        initial_amount = main_page.get_cart_amount()
        main_page.logger.info(f"Сумма в корзине перед добавлением: {initial_amount}₽")

    with allure.step("Пролистать слайдер на 2 позиции вправо"):
        main_page.navigate_to_slide(2)

    with allure.step("Добавить пиццу из текущей позиции слайдера в корзину"):
        main_page.add_pizza_from_current_slide()

    with allure.step("Проверить что сумма в корзине увеличилась"):
        page.wait_for_timeout(2000)

        new_amount = main_page.get_cart_amount()
        main_page.logger.info(f"Сумма в корзине после добавления: {new_amount}₽")

        assert new_amount > initial_amount, (
            f"Сумма в корзине не увеличилась! Было: {initial_amount}₽, Стало: {new_amount}₽"
        )


@allure.title("TC-05: Переход к странице деталей товара 'Ветчина и грибы'")
@pytest.mark.order(5)
def test_navigate_to_product_details(page, main_page, product_page):
    logger.info("ТЕСТ 5: Начало выполнения")

    with allure.step("Кликнуть на второй товар в слайдере ('Ветчина и грибы')"):
        main_page.click_product_by_visible_index(4)

    with allure.step("Проверить что открылась страница с деталями товара"):
        page.wait_for_timeout(2000)

        assert product_page.is_product_page_loaded(), "Страница товара не загрузилась"

        product_title = product_page.get_product_title()
        assert product_title, f"Не найден заголовок товара. Заголовок: {product_title}"

        logger.info(f"Успешно перешли на страницу товара: {product_title}")

    with allure.step("Проверить что URL соответствует странице товара"):
        assert "/product/" in page.url, f"URL не соответствует странице товара: {page.url}"


@allure.title("TC-06: Выбор опции товара и добавление в корзину")
@pytest.mark.order(6)
def test_select_option_and_add_to_cart(page, product_page):
    logger.info("ТЕСТ 6: Начало выполнения")

    with allure.step("Проверить что находимся на странице товара"):
        if "/product/" not in page.url:
            pytest.fail("Тест TC-06 должен выполняться после TC-05 (страница товара должна быть открыта)")

    with allure.step("Запомнить выбранный тип борта по умолчанию"):
        initial_board = product_page.get_selected_board_option()
        logger.info(f"Тип борта по умолчанию: {initial_board}")

    with allure.step("Выбрать опцию 'Сырный борт' из выпадающего списка"):
        product_page.select_board_option("cheese")

        selected_board = product_page.get_selected_board_option()
        assert selected_board == "cheese", f"Опция не выбрана. Текущая: {selected_board}"

    with allure.step("Нажать кнопку 'В корзину' на странице товара"):
        product_page.add_to_cart()

    with allure.step("Проверить что товар добавлен в корзину (появление сообщения)"):
        page.wait_for_timeout(2000)

        button_text = page.text_content(product_page.ADD_TO_CART_BUTTON)
        logger.info(f"Состояние кнопки после добавления: {button_text}")

        success_message = page.locator(".woocommerce-message").is_visible()
        if success_message:
            logger.info("Товар успешно добавлен в корзину")


@allure.title("TC-07: Отображение состава корзины")
@pytest.mark.order(7)
def test_cart_contents_display(page, main_page, cart_page):
    logger.info("ТЕСТ 7: Начало выполнения")

    with allure.step("Перейти в корзину через ссылку в шапке"):
        if "pizzeria.skillbox.cc" not in page.url:
            main_page.open()

        main_page.go_to_cart()

    with allure.step("Проверить что открылась страница корзины"):
        assert "/cart/" in page.url, f"Не открылась страница корзины. Текущий URL: {page.url}"
        assert cart_page.is_cart_empty() is False, "Корзина пуста, но должна содержать товары"

    with allure.step("Проверить что в корзине 3 различных товара"):
        items_count = cart_page.get_cart_items_count()
        logger.info(f"Количество товаров в корзине: {items_count}")
        assert items_count == 3, f"Ожидалось 3 товара, но найдено: {items_count}"

    with allure.step("Проверить названия товаров в корзине"):
        product_names = cart_page.get_product_names()
        logger.info(f"Товары в корзине: {product_names}")
        assert len(product_names) == 3, f"Ожидалось 3 названия товаров, но найдено: {len(product_names)}"

        unique_names = set(product_names)
        assert len(unique_names) == 3, f"Товары не уникальны. Найдены дубликаты: {product_names}"

    with allure.step("Проверить общую стоимость заказа"):
        total_amount = cart_page.get_cart_total_amount()
        logger.info(f"Общая сумма заказа: {total_amount}₽")
        assert total_amount > 0, f"Общая сумма должна быть больше 0, но равна: {total_amount}₽"
        assert total_amount >= 1000, f"Сумма кажется слишком маленькой для 3 товаров: {total_amount}₽"


@allure.title("TC-08: Изменение количества товара в корзине")
@pytest.mark.order(8)
def test_update_cart_quantity(page, cart_page):
    logger.info("ТЕСТ 8: Начало выполнения")

    with allure.step("Проверить что находимся на странице корзины"):
        if "/cart/" not in page.url:
            cart_page.open()

    with allure.step("Запомнить исходные данные корзины перед изменением"):
        initial_total = cart_page.get_cart_total_amount()
        initial_quantity = cart_page.get_product_quantity(0)
        initial_subtotal = cart_page.get_product_subtotal(0)

        logger.info(
            f"Исходные данные: общая сумма={initial_total}₽, "
            f"количество 1го товара={initial_quantity}, сумма за 1й товар={initial_subtotal}₽")

    with allure.step("Изменить количество первого товара на 2"):
        cart_page.update_product_quantity(0, 2)

        page.click("body")
        page.wait_for_timeout(500)

    with allure.step("Нажать кнопку 'Обновить корзину'"):
        cart_page.click_update_cart()

    with allure.step("Проверить что количество товара изменилось"):
        new_quantity = cart_page.get_product_quantity(0)
        assert new_quantity == 2, f"Количество не изменилось. Ожидалось: 2, Фактически: {new_quantity}"
        logger.info(f"Количество товара успешно изменено на: {new_quantity}")

    with allure.step("Проверить что сумма за позицию пересчиталась"):
        new_subtotal = cart_page.get_product_subtotal(0)
        expected_subtotal = initial_subtotal * 2

        assert abs(new_subtotal - expected_subtotal) < 1, (
            f"Сумма за позицию неверно пересчиталась. "
            f"Было: {initial_subtotal}₽, Стало: {new_subtotal}₽, Ожидалось: {expected_subtotal}₽"
        )
        logger.info(f"Сумма за позицию пересчитана: {new_subtotal}₽")

    with allure.step("Проверить что общая сумма заказа пересчиталась"):
        new_total = cart_page.get_cart_total_amount()

        assert new_total > initial_total, (
            f"Общая сумма не увеличилась. Было: {initial_total}₽, Стало: {new_total}₽"
        )
        logger.info(f"Общая сумма заказа пересчитана: {new_total}₽")


@allure.title("TC-09: Удаление товара из корзины")
@pytest.mark.order(9)
def test_remove_product_from_cart(page, cart_page):
    logger.info("ТЕСТ 9: Начало выполнения")

    with allure.step("Проверить что находимся на странице корзины"):
        if "/cart/" not in page.url:
            cart_page.open()

    with allure.step("Запомнить исходные данные корзины перед удалением"):
        initial_items_count = cart_page.get_cart_items_count()
        initial_total = cart_page.get_cart_total_amount()
        initial_product_names = cart_page.get_product_names()

        logger.info(f"Исходные данные: {initial_items_count} товаров, общая сумма={initial_total}₽")
        logger.info(f"Товары в корзине: {initial_product_names}")

    with allure.step("Удалить первый товар из корзины"):
        cart_page.remove_product(0)

        page.wait_for_timeout(2000)

    with allure.step("Проверить что количество товаров уменьшилось на 1"):
        new_items_count = cart_page.get_cart_items_count()
        expected_count = initial_items_count - 1

        assert new_items_count == expected_count, (
            f"Количество товаров не уменьшилось. Было: {initial_items_count}, "
            f"Стало: {new_items_count}, Ожидалось: {expected_count}"
        )
        logger.info(f"Количество товаров уменьшилось: {new_items_count}")

    with allure.step("Проверить что общая сумма уменьшилась"):
        new_total = cart_page.get_cart_total_amount()

        assert new_total < initial_total, (
            f"Общая сумма не уменьшилась после удаления. Было: {initial_total}₽, Стало: {new_total}₽"
        )
        logger.info(f"Общая сумма уменьшилась: {new_total}₽")

    with allure.step("Проверить список оставшихся товаров"):
        remaining_products = cart_page.get_remaining_product_names()
        logger.info(f"Оставшиеся товары: {remaining_products}")

        if initial_product_names:
            removed_product = initial_product_names[0]
            assert removed_product not in remaining_products, (
                f"Удаленный товар '{removed_product}' все еще в корзине"
            )
            logger.info(f"Товар '{removed_product}' успешно удален")

    with allure.step("Проверить что корзина не пуста"):
        assert not cart_page.is_cart_empty(), "Корзина пуста, но должна содержать оставшиеся товары"
        logger.info("В корзине остались другие товары")


@allure.title("TC-10: Фильтрация товаров в каталоге по категории и цене")
@pytest.mark.order(10)
def test_filter_products_by_category_and_price(page, menu_page):
    logger.info("ТЕСТ 10: Начало выполнения")

    with allure.step("Перейти в раздел 'Меню'"):
        menu_page.open()

    with allure.step("Выбрать категорию 'Десерты'"):
        menu_page.select_desserts_category()

    with allure.step("Установить максимальную цену 140 рублей"):
        menu_page.set_max_price(140)

    with allure.step("Нажать кнопку 'Применить' для активации фильтра"):
        apply_button = page.locator("button:has-text('Применить')")
        apply_button.click()
        page.wait_for_timeout(2000)

    with allure.step("Проверить что отображаются товары"):
        products_count = menu_page.get_visible_products_count()
        assert products_count > 0, "После фильтрации не отображаются товары"
        logger.info(f"Отображается товаров: {products_count}")

    with allure.step("Проверить что цены всех товаров не превышают 140 рублей"):
        assert menu_page.are_all_prices_below_max(140), (
            "Найдены товары с ценой выше 140 рублей"
        )

        prices = menu_page.get_product_prices()
        titles = menu_page.get_product_titles()

        for i, (title, price) in enumerate(zip(titles, prices)):
            logger.info(f"Товар {i + 1}: '{title}' - {price}₽")

        logger.info("Все товары соответствуют фильтру цены (<= 140₽)")


@allure.title("TC-11: Добавление товара в корзину из каталога")
@pytest.mark.order(11)
def test_add_product_from_filtered_catalog(page, menu_page, main_page):
    logger.info("ТЕСТ 11: Начало выполнения")

    with allure.step("Проверить что находимся на странице отфильтрованных десертов"):
        if "deserts" not in page.url:
            menu_page.open()
            menu_page.select_desserts_category()
            menu_page.set_max_price(140)
            apply_button = page.locator("button:has-text('Применить')")
            apply_button.click()
            page.wait_for_timeout(2000)

    with allure.step("Запомнить текущую сумму в корзине"):
        initial_amount = main_page.get_cart_amount()
        logger.info(f"Сумма в корзине перед добавлением: {initial_amount}₽")

    with allure.step("Добавить первый отфильтрованный товар в корзину"):
        menu_page.add_product_to_cart(0)

    with allure.step("Проверить что сумма в корзине увеличилась"):
        page.wait_for_timeout(2000)

        new_amount = main_page.get_cart_amount()
        logger.info(f"Сумма в корзине после добавления: {new_amount}₽")

        assert new_amount > initial_amount, (
            f"Сумма в корзине не увеличилась. Было: {initial_amount}₽, Стало: {new_amount}₽"
        )

        price_difference = new_amount - initial_amount
        logger.info(f"Товар успешно добавлен. Сумма увеличилась на: {price_difference}₽")


@allure.title("TC-12: Реакция системы на попытку оформления заказа неавторизованным пользователем")
@pytest.mark.order(12)
def test_guest_checkout_redirects_to_login(page, cart_page):
    logger.info("ТЕСТ 12: Начало выполнения")

    with allure.step("Перейти в корзину и нажать 'Перейти к оплате'"):
        cart_page.open()
        cart_page.proceed_to_checkout()
        page.wait_for_timeout(3000)

    with allure.step("Проверить что отображается блок с предложением авторизации"):
        woo_commerce_info = page.locator("div.woocommerce-info:has-text('Авторизуйтесь')")
        assert woo_commerce_info.is_visible(), "Информационный блок не отображается"

        info_text = woo_commerce_info.text_content()
        logger.info(f"Найден информационный блок: {info_text}")

    with allure.step("Проверить что ссылка 'Авторизуйтесь' отображается и кликабельна"):
        login_link = page.locator("a.showlogin")
        assert login_link.is_visible(), "Ссылка 'Авторизуйтесь' не отображается"

        link_text = login_link.text_content()
        assert "авторизуйтесь" in link_text.lower(), f"Текст ссылки не соответствует: {link_text}"
        logger.info(f"Ссылка 'Авторизуйтесь' найдена: {link_text}")

    with allure.step("Проверить что форма логина изначально скрыта"):
        login_form = page.locator("form.woocommerce-form-login")
        assert not login_form.is_visible(), "Форма логина не должна отображаться до клика"
        logger.info("Форма логина скрыта - корректное поведение")

    with allure.step("Проверить URL страницы"):
        assert "/checkout/" in page.url, f"URL не соответствует странице оформления заказа: {page.url}"
        logger.info(f"Успешно перешли на страницу оформления заказа: {page.url}")


@allure.title("TC-13: Успешная регистрация нового пользователя")
@pytest.mark.order(13)
def test_successful_user_registration(page, account_page):
    logger.info("ТЕСТ 13: Начало выполнения")

    with allure.step("Перейти на страницу 'Мой аккаунт'"):
        account_page.open()

    with allure.step("Нажать на ссылку 'Войти'"):
        account_page.click_login_link()

    with allure.step("Нажать на кнопку 'Зарегистрироваться'"):
        account_page.click_register_button()

    with allure.step("Заполнить форму регистрации"):
        username, email, password = account_page.complete_registration()
        logger.info(f"Данные регистрации: {username}, {email}, пароль: {password}")

    with allure.step("Проверить что регистрация прошла успешно"):
        page.wait_for_timeout(5000)

        error_msg = page.locator(".woocommerce-error")
        if error_msg.is_visible():
            error_text = error_msg.text_content()
            pytest.fail(f"Регистрация не удалась: {error_text}")
        else:
            logger.info(" Регистрация прошла успешно!")

    with allure.step("Сохранить данные пользователя для следующих тестов"):
        user_data = test_data.get_registered_user()

        assert user_data is not None, "Данные пользователя не сохранились"
        assert user_data["username"] == username, "Username не совпадает"
        assert user_data["email"] == email, "Email не совпадает"

        logger.info(f" Данные сохранены: {user_data['username']}, {user_data['email']},"
                    f" пароль: {user_data['password']}")


@allure.title("TC-14: Доступ к форме оформления заказа авторизованным пользователем")
@pytest.mark.order(14)
def test_authorized_user_checkout_access(page, cart_page):
    logger.info("ТЕСТ 14: Начало выполнения")

    with allure.step("Перейти в корзину"):
        cart_page.open()
        items_count = cart_page.get_cart_items_count()
        assert items_count > 0, "Корзина пуста"
        logger.info(f"В корзине товаров: {items_count}")

    with allure.step("Нажать кнопку 'Перейти к оплате'"):
        cart_page.proceed_to_checkout()
        page.wait_for_timeout(3000)

    with allure.step("Проверить что открылась форма оформления заказа"):
        assert "/checkout/" in page.url, f"Не перешли на страницу оформления. URL: {page.url}"
        logger.info("Успешно перешли на страницу оформления заказа")

        form_exists = page.is_visible("form.checkout") or page.is_visible("#customer_details")
        assert form_exists, "Форма оформления заказа не найдена"
        logger.info("Форма оформления заказа отображается")

        login_suggestion = page.locator("div.woocommerce-info:has-text('Авторизуйтесь')")
        if login_suggestion.is_visible():
            pytest.fail("Система предлагает авторизоваться, но пользователь уже авторизован")

        logger.info(" Авторизованный пользователь имеет доступ к оформлению заказа")


@allure.title("TC-15: Создание и подтверждение заказа")
@pytest.mark.order(15)
def test_create_and_confirm_order(page, checkout_page):
    logger.info("ТЕСТ 15: Начало выполнения")

    with allure.step("Проверить что находимся на странице оформления заказа"):
        if "/checkout/" not in page.url:
            pytest.fail("Должны быть на странице оформления заказа после TC-14")

    with allure.step("Заполнить форму доставки"):
        checkout_page.fill_delivery_form()
        logger.info(" Форма доставки заполнена")

    with allure.step("Выбрать дату доставки на завтра"):
        checkout_page.select_delivery_date_tomorrow()
        logger.info(" Дата доставки выбрана")

    with allure.step("Выбрать способ оплаты 'При доставке'"):
        checkout_page.select_cash_on_delivery()
        logger.info(" Способ оплаты выбран")

    with allure.step("Принять условия соглашения"):
        checkout_page.accept_terms()
        logger.info(" Условия приняты")

    with allure.step("Нажать кнопку 'Подтвердить заказ'"):
        initial_url = page.url
        checkout_page.place_order()

        assert page.url != initial_url, "Не произошло перехода после подтверждения заказа"
        logger.info(" Заказ подтвержден")

    with allure.step("Проверить страницу подтверждения заказа"):
        assert checkout_page.is_order_received(), "Не отображается страница подтверждения заказа"

        order_number = checkout_page.get_order_number()
        order_total = checkout_page.get_order_total()

        logger.info(f" Заказ №{order_number} успешно оформлен")
        logger.info(f" Итоговая сумма: {order_total}")

        assert order_total, "Не удалось получить сумму заказа"
        logger.info(" Данные заказа корректны")

    with allure.step("Сделать скриншот подтверждения"):
        page.screenshot(path="screenshots/order_confirmation.png")
        logger.info(" Скриншот подтверждения сохранен")

    logger.info(" ТЕСТОВЫЙ СЦЕНАРИЙ ЗАВЕРШЕН УСПЕШНО!")
