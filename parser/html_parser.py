# part 4
from typing import List

import pandas as pd
import requests as rq
from bs4 import BeautifulSoup
from dateutil import parser
from loguru import logger
from newspaper import Article

from config import Config


class HtmlParser:
    """
    Diese Klasse ist verantwortlich für das Parsen von HTML-Seiten. Sie nutzt verschiedene
    Techniken und Bibliotheken, um Daten aus Webseiten zu extrahieren.
    """
    def __init__(self):
        """
        Initialisiert die HtmlParser-Instanz und konfiguriert den Logger.
        """
        self.config = Config()
        self.config.initialize_logger(package="requests")

    # 4.1
    @staticmethod
    def _get_soup(url):
        """
        Erzeugt ein BeautifulSoup-Objekt aus dem Inhalt einer gegebenen URL.

        Args:
            url (str): URL der Webseite, die geparst werden soll.

        Returns:
            BeautifulSoup: Ein BeautifulSoup-Objekt oder None, falls ein Fehler auftritt.
        """
        req = rq.get(url)
        if req.status_code == 200:
            logger.info(f"parsing url -> {url}")
            soup = BeautifulSoup(req.content, "html.parser")
            return soup
        else:
            logger.error(f"the page cannot be parsed. status code -> {req.status_code}")
            return None

    def get_links_from_main_urls(self, main_urls_list: List):
        """
        Extrahiert Links von Webseiten, die in der übergebenen Liste spezifiziert sind.

        Args:
            main_urls_list (List): Eine Liste von URLs und zugehörigen Informationen.

        Returns:
            List: Die aktualisierte Liste mit extrahierten Links.
        """
        for url_dict in main_urls_list:
            if url_dict["bs4"]:
                sub_urls_list = []
                for url in url_dict["url"]:
                    soup = self._get_soup(url=url)
                    if soup and url_dict.get("a_tag_location"):
                        try:
                            sub_links_raw = soup.findAll(
                                "a", class_=url_dict["a_tag_location"]
                            )
                            sub_links = [
                                a["href"]
                                for a in sub_links_raw
                                if self.config.block_urls_domain not in a["href"]
                            ]
                            sub_urls_list += sub_links
                            logger.info(
                                f"the number of sublink added -> {len(sub_urls_list)} for url {url}"
                            )
                        except (AttributeError, Exception) as err:
                            logger.error(f"sublink could not be found {err}")
                    else:
                        logger.error(f"the page cannot be parsed/a_tag_location key is missing")
                url_dict["sublinks"] = sub_urls_list
        return main_urls_list

    def get_articles_with_newspaper(self, main_urls_list: List) -> List:
        """
        Verwendet die Newspaper3K-Bibliothek, um Artikel von Webseiten zu extrahieren.

        Args:
            main_urls_list (List): Eine Liste von Dictionaries, die URLs und relevante Informationen enthalten.

        Returns:
            List: Eine Liste von Pandas DataFrames, die Informationen zu den extrahierten Artikeln enthalten.
        """
        articles_final_list = []
        articles_list = []
        for url_dict in main_urls_list:
            if url_dict.get("newspaper3K") and len(url_dict["sublinks"]) > 0:
                logger.info(f"articles found : {len(url_dict['sublinks'])} for url {url_dict['url']}")

                for link in url_dict["sublinks"]:
                    logger.info(f"downloading article : {link}")
                    article = Article(link)
                    article.download()
                    article.parse()
                    # Erstellen eines Dictionaries mit Artikelinformationen
                    article_dict = {
                        "name": url_dict["name"],
                        "article_link": link,
                        "title": article.title,
                        "date": article.publish_date if article.publish_date
                        else self._get_date(
                            url=link,
                            date_tag=url_dict["date_tag"],
                            date_location=url_dict["date_location"],
                        ),
                        "article": article.text,
                    }

                    # Überprüfen, ob der Artikelinhalt gefunden wurde
                    article_found = article_dict.get("article")
                    if article_found:
                        articles_list.append(article_dict)
                        logger.success("downloading successful! article added to list")
                    else:
                        logger.warning("article not found!")

        articles_final_list.append(pd.DataFrame(articles_list))
        return articles_final_list

    @staticmethod
    def get_tables_from_html(main_urls_list: List) -> List:
        """
        Extrahiert Tabellen von Webseiten unter Verwendung von Pandas' read_html.

        Args:
            main_urls_list (List): Eine Liste von Dictionaries, die URLs und relevante Informationen enthalten.

        Returns:
            List: Eine Liste von Pandas DataFrames, die die extrahierten Tabellen enthalten.
        """
        tables_list = []
        for url_dict in main_urls_list:
            if url_dict.get('pandas') and url_dict["pandas"]:
                try:
                    url = url_dict['url'][0] if isinstance(url_dict["url"], list) else url_dict['url']
                    table_dfs_list = pd.read_html(url)
                    logger.info(f'Total tables: {len(table_dfs_list)}')

                    # Hinzufügen des Namens der Quellseite zu jeder Tabelle
                    for table_df in table_dfs_list:
                        table_df['name'] = url_dict["name"]
                        tables_list.append(table_df)
                except Exception as e:
                    logger.error(f"Error reading HTML tables from {url}: {e}")
            else:
                logger.error("Pandas key not found or the value is not valid")

        return tables_list

    def _get_date(self, url, date_tag: str, date_location: str):
        """
        Versucht, das Datum eines Artikels von einer Webseite zu extrahieren.

        Args:
            url (str): URL des Artikels.
            date_tag (str): HTML-Tag, das das Datum enthält.
            date_location (str): Klasse oder ID des HTML-Tags.

        Returns:
            str: Das extrahierte Datum als String oder None, falls kein Datum gefunden wurde.
        """
        # Erstellen Sie ein BeautifulSoup-Objekt
        logger.info(f"article date is being scraped manually")
        if date_tag and date_location:
            soup = self._get_soup(url=url)
            if soup:
                # das erste Element wird gefunden
                date_element = soup.find(date_tag, class_=date_location)
                if date_element:
                    date_text = date_element.get_text(strip=True)
                    logger.info(f"date extracted -> {date_text}")
                    try:
                        date_formatted = parser.parse(date_text).strftime("%d-%m-%Y")
                        return date_formatted
                    except (AttributeError, ValueError, Exception) as err:
                        logger.error(f"date could not be formatted -> {err}")

                        return date_text
                else:
                    logger.warning(f"date could not be extracted!")
                    return None
            else:
                logger.error(
                    f"the article link could not be parsed for date extraction!"
                )
                return None
