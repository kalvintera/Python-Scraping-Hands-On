import random
import time
from typing import List

import newspaper
import pandas as pd
import requests as rq
from bs4 import BeautifulSoup
from loguru import logger
from newspaper import Article

from config import Config


class HtmlParser:
    """
    Diese Klasse ist verantwortlich für das Parsen von HTML-Seiten. Sie nutzt verschiedene
    Techniken und Bibliotheken, um Daten aus Webseiten zu extrahieren.
    """

    def __init__(self, config: Config):
        """
        Initialisiert die HtmlParser-Instanz und konfiguriert den Logger.
        """
        self.config = config
        # self.config.initialize_logger()

    def _get_soup(self, url: str) -> BeautifulSoup | None:
        """
        Erzeugt ein BeautifulSoup-Objekt aus dem Inhalt einer gegebenen URL.

        Args:
            url (str): URL der Webseite, die geparst werden soll.

        Returns:
            BeautifulSoup: Ein BeautifulSoup-Objekt oder None, falls ein Fehler auftritt.
        """
        req = rq.get(url, headers=self.config.headers)
        if req.status_code == 200:
            logger.info(f"parsing url -> {url}")
            soup = BeautifulSoup(req.content, "html.parser")
            return soup
        else:
            logger.error(f"the page cannot be parsed. status code -> {req.status_code}")
            return None

    def get_links_from_main_urls(self, main_urls_list: List) -> List:
        """
        Extrahiert Links von Webseiten, die in der übergebenen Liste spezifiziert sind.

        Args:
            main_urls_list (List): Eine Liste von URLs und zugehörigen Informationen.

        Returns:
            List: Die aktualisierte Liste mit extrahierten Links.
        """
        for url_dict in main_urls_list:
            if url_dict.get("bs4", None):
                sub_urls_list = []
                for url in url_dict["url"]:
                    soup = self._get_soup(url=url)
                    a_tag_location = url_dict.get("a_tag_location_css")
                    if soup and a_tag_location:

                        try:
                            sub_links_raw = soup.findAll("a", class_=a_tag_location)
                            sub_links = [a["href"] for a in sub_links_raw]
                            sub_urls_list += sub_links
                            logger.info(
                                f"the number of sublink added -> {len(sub_urls_list)} for url {url}"
                            )
                        except (AttributeError, Exception) as err:
                            logger.error(f"sublink could not be found {err}")
                    else:
                        logger.error(
                            f"the page cannot be parsed/a_tag_location key is missing"
                        )
                url_dict["sublinks"] = sub_urls_list
        return main_urls_list

    @staticmethod
    def get_articles_with_newspaper(
        main_urls_list: List, n_articles: int = None
    ) -> List:
        """
        Verwendet die Newspaper3K-Bibliothek, um Artikel von Webseiten zu extrahieren.

        Args:
            main_urls_list (List): Eine Liste von Dictionaries, die URLs und relevante Informationen enthalten.
            n_articles (int): Die Anzahl der Links, die von jeder Liste gescraped werden sollen

        Returns:
            List: Eine Liste von Pandas DataFrames, die Informationen zu den extrahierten Artikeln enthalten.
        """
        articles_final_list = []

        for url_dict in main_urls_list:
            articles_list = []

            if url_dict.get("newspaper3K", None) and len(url_dict.get("sublinks", [])) > 0:
                logger.info(
                    f"articles found : {len(url_dict['sublinks'])} for url {url_dict['url']}"
                )
                # Anzahl der Links werden manuell bestimmt

                for link in url_dict["sublinks"]:
                    logger.info(f"downloading article : {link}")

                    try:
                        article = Article(link)

                        # random sleep mit einem Minimum Sleep Wert von 2 Sekunden
                        time.sleep(2 + random.randint(0, 2))

                        article.download()
                        article.parse()

                        # Erstellen eines Dictionaries mit Artikelinformationen
                        article_dict = {
                            "name": url_dict["name"],
                            "article_link": link,
                            "title": article.title,
                            "date": article.publish_date,
                            "article": article.text,
                            "tags": (
                                "#" + " #".join(article.tags) if article.tags else ""
                            ),
                        }

                        # Überprüfen, ob der Artikelinhalt gefunden wurde
                        article_found = article_dict.get("article")
                        if article_found:
                            articles_list.append(article_dict)
                            logger.success(
                                "downloading successful! article added to list"
                            )
                        else:
                            logger.warning("article not found!")

                        if n_articles and len(articles_list) >= n_articles:
                            break

                    except (Exception, newspaper.ArticleException) as err:
                        logger.error(
                            f"Something went wrong while parsing {link} - Error: {err}"
                        )

                articles_final_list.append(pd.DataFrame(articles_list))

        return articles_final_list

    @staticmethod
    def get_tables_from_html(main_urls_list: List) -> List:
        """
        Extrahiert Tabellen von Webseiten unter Verwendung von Panda's read_html.

        Args:
            main_urls_list (List): Eine Liste von Dictionaries, die URLs und relevante Informationen enthalten.

        Returns:
            List: Eine Liste von Pandas DataFrames, die die extrahierten Tabellen enthalten.
        """
        tables_list = []
        for url_dict in main_urls_list:
            if url_dict["pandas"]:
                try:

                    table_dfs_list = pd.read_html(url_dict["url"])
                    logger.info(f"Total tables: {len(table_dfs_list)}")

                    # Hinzufügen des Namens der Quellseite zu jeder Tabelle
                    for index, table_df in enumerate(table_dfs_list):
                        table_df["name"] = f"{url_dict['name']}_Table_{index}"
                        tables_list.append(table_df)
                except Exception as e:
                    logger.error(
                        f"Error reading HTML tables from {url_dict['url']}: {e}"
                    )
            else:
                logger.warning("Pandas key not found in config dict or the value is not valid")

        return tables_list
