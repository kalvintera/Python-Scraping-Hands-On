# third part
import time
from typing import List

from loguru import logger
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from config import Config


class DynamicPageHandler:
    """
    Klasse zur Handhabung dynamischer Webseiten, insbesondere für das Scraping von paginierten Inhalten.

    Attributes:
        config (Config): Eine Instanz der Konfigurationsklasse.
    """

    def __init__(self):
        """
        Initialisiert die DynamicPageHandler-Instanz und setzt die Logger-Konfiguration.
        """
        self.config = Config()
        self.config.initialize_logger()

    # 3.1
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

        for url_dict in main_urls_list:
            # Überprüfung, ob Paginierungsinformationen vorhanden sind
            if url_dict["paginated"] and url_dict["page_button_location"]:
                options = webdriver.ChromeOptions()
                options.add_argument("--headless")
                # Definiert die Ladestrategie für den Seiteninhalt
                options.page_load_strategy = "eager"
                driver = webdriver.Chrome(
                    service=ChromeService(ChromeDriverManager().install()),
                    options=options,
                )
                pages_links = url_dict["url"]
                driver.get(url_dict["url"][0])
                logger.info("Warte 10 Sekunden, um eine Bedingung zu erfüllen.")

                # Initialisierung des Wartevorgangs
                wait = WebDriverWait(driver, 10)

                # Schleife zur Durchquerung der paginierten Seiten
                pagination_stop = False
                page_count = 0
                while not pagination_stop and page_count < 2:
                    try:
                        pagination_button = driver.find_element(
                            By.XPATH, url_dict["page_button_location"]
                        )
                        # Scrollt zur Paginierungsschaltfläche
                        driver.execute_script(
                            "arguments[0].scrollIntoView();", pagination_button
                        )
                        logger.info("Warte auf das Klick-Element.")
                        time.sleep(5)
                        wait.until(
                            EC.element_to_be_clickable(
                                (By.XPATH, url_dict["page_button_location"])
                            )
                        )
                        # Klick auf die nächste Seite
                        pagination_button.click()
                        new_page = driver.current_url
                        logger.success("Schaltfläche geklickt!")
                        pages_links.append(new_page)
                        page_count += 1
                        logger.info(f"Seite {page_count} wird gecrawlt.")
                    except NoSuchElementException as err:
                        logger.error(f"Paginierungsschaltfläche nicht gefunden: {err}")
                        pagination_stop = True

                url_dict["url"] = pages_links
                logger.info(f"{len(url_dict['url']) - 1} neue Seiten zu {url_dict['url'][0]} hinzugefügt")

            else:
                logger.warning("Keine Paginierungsinformationen verfügbar.")

        return main_urls_list