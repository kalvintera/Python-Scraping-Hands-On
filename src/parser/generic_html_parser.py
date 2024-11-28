import time
from typing import List

from loguru import logger
from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementNotInteractableException,
    ElementClickInterceptedException,
    TimeoutException,
)
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# OPTIONAL - Cache Management


from config import Config


class DynamicPageHandler:
    """
    Klasse zur Handhabung dynamischer Webseiten, insbesondere für das Scraping von paginierten Inhalten.

    Attributes:
        config (Config): Eine Instanz der Konfigurationsklasse.
    """

    def __init__(self, config: Config):
        """
        Initialisiert die DynamicPageHandler-Instanz und setzt die Logger-Konfiguration.
        """
        self.config = config

    @staticmethod
    def get_paginated_links(main_urls_list: List) -> List:
        """
        Extrahiert Links von paginierten Webseiten.

        Geht durch eine Liste von URLs und extrahiert Links von Seiten, die eine Paginierung aufweisen.

        Args:
            main_urls_list (List): Eine Liste von Dictionaries, die URLs und Paginierungs-Informationen enthalten.

        Returns:
            List: Die aktualisierte Liste mit den extrahierten URLs für jede Seite.
        """

        options = webdriver.ChromeOptions()
        # Headless ist ein Ausführungsmodus für Firefox- und Chromium-basierte Browser.
        # was bedeutet, dass das Browserfenster nicht sichtbar ist.
        options.add_argument("--headless")

        # Definiert die Ladestrategie für den Seiteninhalt
        options.page_load_strategy = "eager"
        # driver = webdriver.Chrome(options=options)
        """
        
        """
        driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=options,
        )  # cache_manager=self.cache_manager

        # Initialisierung des Wartevorgangs
        wait = WebDriverWait(driver, 10)

        for url_dict in main_urls_list:
            # Überprüfung, ob Paginierungsinformationen vorhanden sind
            if url_dict["paginated"] and url_dict["page_button_location"]:

                pages_links = [url_dict["url"]]
                logger.info(
                    f"The Method driver.get navigates to page {url_dict['url']}"
                )
                driver.get(url_dict["url"])

                # Schleife zur Durchquerung der paginierten Seiten
                pagination_stop = False
                page_count = 0
                # Extrahiere "Next" Button Locations vom URL-DICT
                pagination_xpath_initial = url_dict["page_button_location"].get(
                    "initial", None
                )
                pagination_xpath_next = url_dict["page_button_location"].get(
                    "second", None
                )

                while not pagination_stop and page_count < 2:

                    pagination_xpath = (
                        pagination_xpath_initial
                        if page_count == 0
                        else pagination_xpath_next
                    )
                    try:
                        pagination_button = driver.find_element(
                            By.XPATH, pagination_xpath
                        )
                        # Scrollt zum Button
                        driver.execute_script(
                            "arguments[0].scrollIntoView();", pagination_button
                        )
                        logger.info("waiting for button element...")
                        time.sleep(1)

                        wait.until(EC.element_to_be_clickable(pagination_button))

                        # Klick auf die nächste Seite
                        pagination_button.click()
                        logger.success("button clicked!")
                        # Aktuelle Seite:
                        new_page = driver.current_url

                        pages_links.append(new_page)
                        page_count += 1
                        logger.info(f"page {page_count} crawled.")
                    except (
                        NoSuchElementException,
                        ElementNotInteractableException,
                        ElementClickInterceptedException,
                        TimeoutException,
                    ) as err:
                        logger.error(f"pagination button not found {err}")
                        pagination_stop = True

                url_dict["url"] = pages_links
                logger.info(
                    f"{len(url_dict['url']) - 1} new pages added to {url_dict['url']}"
                )
                # Browser schließen
                driver.quit()

            else:
                logger.warning("There is no pagination button information is missing")

        return main_urls_list
