import logging
from dataclasses import dataclass
from pathlib import Path
from fake_useragent import UserAgent

ua = UserAgent()


@dataclass
class Config:
    """
    Konfigurationsklasse für den Web-Scraper.
    Enthält Pfade, Einstellungen und Konstanten, die im gesamten Projekt verwendet werden.

    Attributes:
        project_path (Path): Pfad zum Wurzelverzeichnis des Projekts.
        urls_csv_path (Path): Pfad zur CSV-Datei mit URLs und weiteren Informationen.
        urls_json_path (Path): Pfad zur JSON-Datei mit URLs und weiteren Informationen.
        output_path (Path): Pfad zum Verzeichnis für Ausgabedateien.
        delimiter (str): Trennzeichen für CSV-Dateien.
        encoding (str): Zeichenkodierung für Dateien.
        boolean_cols (list): Liste von Spaltennamen, die boolesche Werte enthalten.
    """

    project_path: Path = Path(__file__).parent.resolve()
    urls_csv_path: Path = project_path.joinpath("urls.csv")
    urls_json_path: Path = project_path.joinpath("urls.json")
    output_path: Path = project_path.joinpath("output")
    delimiter: str = ";"
    encoding: str = "utf-8"

    boolean_cols = [
        "selenium",
        "pandas",
        "bs4",
        "newspaper3K",
        "paginated"
    ]

    headers = {
        "User-Agent": ua.random,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    }

    @staticmethod
    def initialize_logger(package: str = None):
        """
        Initialisiert und konfiguriert den Logger für das angegebene Paket oder das Root-Logger.

        Args:
            package (str, optional): Der Name des Pakets, für das der Logger konfiguriert werden soll.
                                     Falls None, wird der Root-Logger konfiguriert.
        """
        logger = logging.getLogger(package) if package else logging.getLogger()
        logger.setLevel(logging.DEBUG)

        # Stellt sicher, dass kein doppelter Handler hinzugefügt wird.
        if not logger.handlers:
            # Erstellt einen StreamHandler, der die Log-Nachrichten in der Konsole ausgibt.
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
            )
            logger.addHandler(stream_handler)
