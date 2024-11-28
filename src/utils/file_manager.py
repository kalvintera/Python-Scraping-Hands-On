import datetime
from typing import List
from loguru import logger
import numpy as np
import pandas as pd

from config import Config


class FileHandler:
    """
    Eine Klasse zur Handhabung der Konfigurationsdateien im CSV- und JSON-Format.
    Sie liest Konfigurationsdaten aus diesen Dateien und konvertiert sie in eine nutzbare Form.
    """

    def __init__(self, config: Config):
        """
        Initialisiert die FileHandler-Instanz und lädt die Konfigurationseinstellungen.
        """
        self.config = config

    def create_main_url_dict_from_json(self) -> List:
        """
        Liest eine JSON-Konfigurationsdatei ein und konvertiert sie in eine Liste von Dictionaries.

        Returns:
            List: Eine Liste von Dictionaries, die Konfigurationsdaten enthalten.
        """
        main_urls_df = pd.read_json(self.config.urls_json_path)

        main_urls_list = main_urls_df.to_dict("records")
        return main_urls_list

    def create_main_url_dict_from_csv(self) -> List:
        """
        Liest eine CSV-Konfigurationsdatei ein und konvertiert sie in eine Liste von Dictionaries.

        Returns:
            List: Eine Liste von Dictionaries, die Konfigurationsdaten enthalten.
        """
        main_urls_df = pd.read_csv(
            self.config.urls_csv_path,
            delimiter=self.config.delimiter,
            encoding=self.config.encoding,
        ).reset_index(drop=True)

        # Stellt sicher, dass URLs als Listen formatiert sind
        main_urls_df["url"] = main_urls_df["url"].apply(
            lambda x: [x] if not isinstance(x, list) else x
        )

        # Konvertiert boolesche Werte
        main_urls_df[self.config.boolean_cols] = main_urls_df[self.config.boolean_cols].astype('bool')

        main_urls_list = main_urls_df.to_dict("records")
        return main_urls_list

    def export_collection_to_csv(self, output_df_list: List) -> None:
        """
        Exportiert eine Sammlung von DataFrames oder Dictionaries als CSV-Dateien.

        Args:
            output_df_list (List): Eine Liste von DataFrames oder Dictionaries.

        Returns:
            None
        """
        if output_df_list:
            logger.success("data is being exported as csv...")
            for output in output_df_list:
                if isinstance(output, pd.DataFrame) and not output.empty:
                    name = output['name'].iloc[0]
                    output = output.replace({np.nan: None}).reset_index(drop=True)
                    output.to_csv(
                        self.config.output_path.joinpath(
                            f"{name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                        ),
                        encoding=self.config.encoding,
                        sep=self.config.delimiter,
                        index=False
                    )
                    logger.success(f"dataframe {name} exported successfully")
                else:
                    logger.warning("dataframe is empty or the output is not a dataframe")

        else:
            logger.warning("the output list is empty")


