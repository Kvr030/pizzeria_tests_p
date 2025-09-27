import time
import sys
import pytest
from utilities.logger import logger


def run_tests_sequence():

    test_suites = [
        {
            "name": "Основной флоу",
            "file": "tests/test_main_flow.py",
            "description": "15 основных тест-кейсов пользовательского флоу"
        },
        {
            "name": "Промокоды",
            "file": "tests/test_promocodes.py",
            "description": "4 сценария работы с промокодами"
        },
        {
            "name": "Бонусная программа",
            "file": "tests/test_bonus_flow.py",
            "description": "Регистрация в бонусной программе"
        }
    ]

    logger.info(" Начало выполнения всех тестовых сценариев")
    start_time = time.time()

    for i, suite in enumerate(test_suites, 1):
        logger.info(f"\n{'=' * 60}")
        logger.info(f" {i}. Запуск: {suite['name']}")
        logger.info(f" Описание: {suite['description']}")
        logger.info(f" Файл: {suite['file']}")
        logger.info(f"{'=' * 60}")

        try:
            original_argv = sys.argv.copy()

            sys.argv = [
                "pytest",
                suite["file"],
                "-v",
                "--alluredir=allure-results",
                "--tb=short"
            ]

            exit_code = pytest.main()

            sys.argv = original_argv

            if exit_code == 0:
                logger.info(f" Тесты {suite['name']} успешно завершены")
            else:
                logger.error(f" Тесты {suite['name']} завершились с ошибками (код: {exit_code})")

        except Exception as e:
            logger.error(f" Ошибка при запуске тестов {suite['name']}: {e}")
            continue

    end_time = time.time()
    duration = end_time - start_time
    logger.info(f"\n{'=' * 60}")
    logger.info(" Все тесты завершены!")
    logger.info(f"  Общее время выполнения: {duration:.2f} секунд")
    logger.info(" Отчеты сохранены в: allure-results/")
    logger.info(f"{'=' * 60}")


if __name__ == "__main__":
    run_tests_sequence()