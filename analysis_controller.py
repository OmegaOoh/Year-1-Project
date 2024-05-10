""" Analysis Controller Module for Analysis Application
This module is responsible for invoke the function in model and return the data to the UI"""
import pandas as pd
from matplotlib.figure import Figure
from pandas import DataFrame
from analysis_model import Analysis


class AnalysisController:
    """ Controller for analysis application"""
    def __init__(self, csv_name):
        self.__model = Analysis(csv_name)

    def get_df(self) -> DataFrame:
        """ Return copy of dataframe"""
        return self.__model.df.df.copy()

    def get_raw(self):
        """ Return the copy of raw dataframe """
        return self.__model.df.get_raw()

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
        """ Counts number of occurrences between time interval (Need to convert to datetime format first)
        :param str interval: time interval (datetime interval)
        :return DataFrame: dataframe of counted value grouped by time interval
        """
        return self.__model.to_timeseries_count(interval)

    def mean_time(self, column: str = 'Price', interval: str = 'YE') -> DataFrame:
        """ Counts number of occurrences between time interval (Need to convert to datetime format first)
        :param str interval: time interval (datetime interval)
        :param str column: column to get mean from
        :return DataFrame: dataframe of mean value grouped by time interval
        """
        return self.__model.to_timeseries_mean(interval, column)

    def apply(self, target_column: str, function, axis=0) -> None:
        """ Apply the given function to the source column and apply the result to target columns
        :param target_column: name of the to save the results to
        :param axis: axis to apply the function to (0 for rows(default), 1 for columns)
        :param function: function to be applies
        """
        self.__model.apply(target_column, function, axis)

    def filter(self, column: str, expression: str) -> None:
        """ Filter values in column based on given expression
            Example of expression: '>= 0', '< 1'
        :param column: column name that need to be filter
        :param expression: expression string for filtering
        """
        self.__model.filter(column, expression)

    def search(self, query: str) -> pd.DataFrame:
        """ Search the data inside entire dataframe, by query
        :param query: the query to search (AppID, Name)
        :return DataFrame: dataframe of search results"""
        return self.__model.search(query)

    def to_list(self, column: str):
        """ Converts data in specified columns to list of strings """
        self.__model.df.to_list(column)

    def get_correlation(self, x: str, y: str):
        """ Calculates the correlation with the given x and y column
        :param x : columns name x
        :param y : columns name y
        :return : correlation coefficient
        """
        return self.__model.get_correlation(x, y)

    def get_picture(self, appid: str):
        return self.__model.get_image(appid)

    def get_specific(self, appid: str) -> pd.DataFrame:
        """ return dictionary contains specific information about the given game
        :param appid: the appid of video game
        :return : Dataframe containing 1 specific game information"""
        return self.__model.get_specific(appid)

    def get_dataframes_name(self):
        return self.__model.get_saved_name()

    def add_to_dataframe(self, content: (pd.Series, pd.DataFrame), name: str) -> None:
        """ Add content to saved dataframe
        :param content: data to add into dataframe
        :param name: name of the dataframe to save to"""
        self.__model.add_to_dataframe(content, name)

    def get_filter_columns(self) -> dict:
        """ return the dictionary containing the column names used for filtering or other operation"""
        return {'num': self.__model.get_num_column(), 'other': self.__model.get_non_numeric_columns()}

    def get_num_column(self) -> list:
        """ return the list of the numerical columns """
        return self.__model.get_num_column()

    def get_non_numeric_columns(self) -> list:
        """ return the list of non-numeric columns """
        return self.__model.get_non_numeric_columns()

    def filter_str(self, col, filter_str) -> None:
        """ filter the dataframe column by given string """
        self.__model.filter_str(col, filter_str)

    def save_all(self) -> None:
        """ save all dataframe to csv file in saved directory """
        self.__model.df.save_all_df()

    def get_unique_genres(self) -> list:
        """ return list of unique genres inside dataframe"""
        return self.__model.get_all_genres()

    def visit_steamdb(self, appid: str = '') -> None:
        """ visit steamdb.info site of specified app"""
        self.__model.open_steamdb(appid)

    def visit_steam(self, appid: str = '') -> None:
        """ visit steam site of specified app"""
        self.__model.open_steam(appid)

    def plot_histogram(self, df: DataFrame, x_column: str, x_label: str, y_label: str,
                       title: str = 'Histogram', bins: int = None) -> Figure:
        """ Plot histogram according to input """
        return self.__model.plot_histogram(df, x_column, x_label, y_label, title, bins)

    def plot_scatter(self, df: DataFrame, x_column: str, y_column: str, x_label: str, y_label: str,
                     title: str = 'Scatter Plot') -> Figure:
        """ Plot the scatter plot of the data """
        return self.__model.plot_scatter(df, x_column, y_column, x_label, y_label, title)

    def plot_line(self, df: DataFrame, x_column: str, y_column: str, x_label: str, y_label: str,
                  title: str = 'Line Plot') -> Figure:
        """ Plot the line plot of the data """
        return self.__model.plot_line(df, x_column, y_column, x_label, y_label, title)

    def plot_pie(self, df: DataFrame, x_column: str,
                 title: str = 'Pie Plot') -> Figure:
        """ Plot the pie plot of the data """
        return self.__model.plot_pie(df, x_column, title)
