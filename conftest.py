import pytest
from playwright.sync_api import sync_playwright
from utilities.logger import logger


@pytest.fixture(scope="session")
def browser():
    logger.info(" Запускаю браузер для тестов")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=1000)
        yield browser
        logger.info(" Закрываю браузер после тестов")
        browser.close()


@pytest.fixture(scope="session")
def context(browser):
    logger.info(" Создаю контекст браузера")
    context = browser.new_context(
        viewport=None,
        base_url="https://pizzeria.skillbox.cc"
    )

    context.set_default_timeout(30000)

    yield context
    logger.info(" Контекст завершен")


@pytest.fixture(scope="session")
def page(context):
    logger.info(" Создаю одну вкладку для всей сессии")
    page = context.new_page()
    yield page
    logger.info(" Закрываю вкладку после всех тестов")


@pytest.fixture(scope="session")
def main_page(page):
    from pages.main_page import MainPage
    return MainPage(page)


@pytest.fixture(scope="session")
def product_page(page):
    from pages.product_page import ProductPage
    return ProductPage(page)


@pytest.fixture(scope="session")
def cart_page(page):
    from pages.cart_page import CartPage
    return CartPage(page)


@pytest.fixture(scope="session")
def menu_page(page):
    from pages.menu_page import MenuPage
    return MenuPage(page)


@pytest.fixture(scope="session")
def checkout_page(page):
    from pages.checkout_page import CheckoutPage
    return CheckoutPage(page)


@pytest.fixture(scope="session")
def account_page(page):
    from pages.account_page import AccountPage
    return AccountPage(page)


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_data():
    yield
    print(" Данные сохранены для следующих запусков тестов")


@pytest.fixture(scope="session")
def bonus_page(page):
    from pages.bonus_page import BonusPage
    return BonusPage(page)
