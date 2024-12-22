import sys
from loguru import logger
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
    print(output_path)
    delimiter: str = ";"
    encoding: str = "utf-8"
    start_headless = False

    boolean_cols = ["selenium", "pandas", "bs4", "newspaper3K", "paginated"]

    headers = {
        "User-Agent": ua.random,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    }

    @staticmethod
    def initialize_logger() -> None:
        """
        Initialisiert und konfiguriert den Logger.

        """

        # Für mehr Info: https://loguru.readthedocs.io/en/stable/api/logger.html
        log_level = "DEBUG"
        log_format = ("<green>{time:YYYY-MM-DD HH:mm:ss.SSS zz}</green> | <level>{level: <8}</level> | <yellow>Line "
                      "{line: >4} ({file}):</yellow> <b>{message}</b>")
        logger.add(sys.stderr, level=log_level, format=log_format, colorize=True, backtrace=True, diagnose=True)

        # spezifische Handler für Fehler und kritische Stufen mit benutzerdefinierten:
        logger.add(
            sys.stderr,
            level="ERROR",
            format="<red>{time:YYYY-MM-DD HH:mm:ss.SSS zz}</red> | <level>{level: <8}</level> | <red>Line {line: >4} "
                   "({file}):</red> <level>{message}</level>",
            colorize=True,
            backtrace=True,
            diagnose=True
        )

        # Warnmeldungen mit Gelb einfärben
        log_format_warning = (
            "<yellow>{time:YYYY-MM-DD HH:mm:ss.SSS zz}</yellow> | "
            "<yellow>{level: <8}</yellow> | "
            "<yellow>Line {line: >4} ({file}):</yellow> "
            "<yellow>{message}</yellow>"
        )

        # sys.stderr -> logging für die Konsole
        logger.add(
            sys.stderr,
            level="WARNING",
            format=log_format_warning,
            colorize=True,
            backtrace=True,
            diagnose=True
        )
        logger.add(
            sys.stderr,
            level="CRITICAL",
            format="<bold red>{time:YYYY-MM-DD HH:mm:ss.SSS zz}</bold red> | <level>{level: <8}</level> | "
                   "<bold red>Line {line: >4} ({file}):</bold red> <level>{message}</level>",
            colorize=True,
            backtrace=True,
            diagnose=True
        )

