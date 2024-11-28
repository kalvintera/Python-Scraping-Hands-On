from src.parser.generic_html_parser import DynamicPageHandler
from src.parser.html_parser import HtmlParser

from src.utils.file_manager import FileHandler
from config import Config


def run():
    """
    Hauptfunktion, die den Web-Scraping-Prozess steuert.

    Liest Konfigurationsdaten, extrahiert URLs, verarbeitet dynamische Seiten,
    extrahiert Artikel und Tabellen und exportiert die Ergebnisse in CSV-Dateien.
    """
    # Initialisierung der Config Klasse
    config = Config()
    config.initialize_logger()

    # Initialisierung der Handler für Dateioperationen und HTML-Verarbeitung
    file_handler = FileHandler(config=config)
    dynamic_page_handler = DynamicPageHandler(config=config)
    html_handler = HtmlParser(config=config)

    # Konfigurationsdaten aus JSON einlesen
    main_urls_list = file_handler.create_main_url_dict_from_json()

    # Verarbeitung von paginierten URLs
    paginated_urls = dynamic_page_handler.get_paginated_links(
        main_urls_list=main_urls_list
    )

    # Extrahieren von Links von den Haupt-URLs
    final_urls_list = html_handler.get_links_from_main_urls(
        main_urls_list=paginated_urls
    )

    # Extrahieren von Artikeln mit Newspaper3K
    articles_list = html_handler.get_articles_with_newspaper(
        main_urls_list=final_urls_list, n_articles=5
    )

    # Extrahieren von Tabelleninhalten von Webseiten
    table_content = html_handler.get_tables_from_html(main_urls_list=main_urls_list)

    # Kombinieren der Ergebnisse aus Artikeln und Tabellen
    result_list = table_content + articles_list

    # Ausgabe der Ergebnisse und Export in CSV-Dateien
    file_handler.export_collection_to_csv(output_df_list=result_list)


if __name__ == "__main__":
    run()
