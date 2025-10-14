from io import UnsupportedOperation
from typing import final
import pandas as pd
from ..config.database.data_connection import _SqlDataConnection


@final
class PlateFrameRepository:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PlateFrameRepository, cls).__new__(cls)
            cls._instance._connection = None
        return cls._instance
    
    def __init__(self):
        if self._connection is None:
            self._connection = _SqlDataConnection()
    
    @property
    def __connection(self):
        return self._connection

    def get_plate_frame(self, plate_frame_name: str):
        return pd.read_sql_query("SELECT * FROM plate_frame WHERE name = ?", self.__connection.db, params=(plate_frame_name,))

    def get_plate_frames(self):
        return pd.read_sql_query("SELECT * FROM plate_frame", self.__connection.db)

    def get_plate_frames_by_plate(self, plate_name: str):
        return pd.read_sql_query("SELECT * FROM plate_frame WHERE plate_name = ?", self.__connection.db, params=(plate_name,))

    @staticmethod
    def _avoid_sql_injection(self, query: str):
        if query.__contains__("--"):
            raise UnsupportedOperation("SQL injection is not allowed")

    @staticmethod
    def __avoid_sql_delete(self, query: str):
        if query.__contains__("DELETE"):
            raise UnsupportedOperation("Delete operation is not allowed")
    
    @staticmethod
    def __avoid_sql_update(query: str):
        if query.__contains__("UPDATE"):
            raise UnsupportedOperation("Update operation is not allowed")
    
    @staticmethod
    def __avoid_sql_insert(query: str):
        if query.__contains__("INSERT"):
            raise UnsupportedOperation("Insert operation is not allowed")

    def get_from_custom_query(self, query: str, params: tuple = None):
        self._avoid_sql_injection(query)
        self.__avoid_sql_delete(query)
        self.__avoid_sql_update(query)
        self.__avoid_sql_insert(query)
        return pd.read_sql_query(query, self.__connection.db, params=params)
    