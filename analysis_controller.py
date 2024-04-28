""" Analysis Controller Module for Analysis Application"""

from pandas import DataFrame
from analysis_model import Analysis


class AnalysisController:
    """ Controller for analysis application"""
    def __init__(self):
        self.__model = Analysis()

    def get_df(self) -> DataFrame:
        """ Return copy of dataframe"""
        return self.__model.df.df.copy()

    def reset_df(self):
        """ Reset dataframe """
        self.__model.df.reset_df()

    def save_df(self, name: str):
        """ Save dataframe """
        self.__model.df.save_df(name)

    def load_df(self, name: str):
        """ load specific dataframe to use"""
        self.__model.df.load_df(name)

    def to_datetime(self) -> None:
        """ Turns dataframe 'release date' column to datetime format """
        self.__model.df.to_datetime()

    def count_time(self, interval: str = 'YE') -> DataFrame:
        """ Counts number of occurrences between time interval (Need to convert to datetime format first) """
        return self.__model.to_timeseries_count(interval)

    def mean_time(self, interval: str = 'YE', column: str = 'Price') -> DataFrame:
        """ Counts number of occurrences between time interval (Need to convert to datetime format first) """
        return self.__model.to_timeseries_mean(interval, column)

    def apply(self, target_column: str, function, axis=0) ->None:
        """ Apply the given function to the source column and apply the result to target columns"""
        self.__model.apply(target_column, function, axis)

    def filter(self, column: str, expression: str) -> None:
        """ Filter values in column based on given expression
            Example of expression: '>= 0', '< 1' """
        self.__model.filter(column, expression)

    def to_list(self, column: str):
        """ Converts data in specified columns to list of strings """
        self.__model.df.to_list(column)
