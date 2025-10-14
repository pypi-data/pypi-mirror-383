import pandas as pd

from ..config.database.data_connection import _SqlDataConnection

class PlateRepository:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PlateRepository, cls).__new__(cls)
            cls._instance._connection = None
        return cls._instance
    
    def __init__(self):
        if self._connection is None:
            self._connection = _SqlDataConnection()
    
    @property
    def __connection(self):
        return self._connection

    def get_plate(self, plate_name: str):
        cursor = self.__get_cursor()
        return pd.read_sql_query("SELECT * FROM plate WHERE name = ?", self.__connection, params=(plate_name,))

    def get_plates(self, plate_name: str):
        return pd.read_sql_query("SELECT * FROM plate", self.__connection)
