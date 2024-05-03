""" Analysis model for all most operation in GUI application"""

import pandas as pd
from PIL import Image
import requests
from io import BytesIO
from dataframesaver import DataFrameSaver as Ds


class Analysis:
    """ Analysis model for all operation in GUI application"""
    def __init__(self):
        self.df = Ds('game_market_data.csv')

    def to_timeseries_count(self, interval: str) -> pd.DataFrame:
        """ returns dataframe that contains count of given column grouped by release date"""
        df = self.df.df.copy()
        df = df.set_index(['Release date'])
        df = df.resample(interval)['Name'].count()
        df = pd.DataFrame(df)
        df.reset_index(inplace=True)
        return df

    def to_timeseries_mean(self, interval: str, column: str) -> pd.DataFrame:
        """ returns dataframe that contains mean of given column grouped by release date"""
        df = self.df.df.copy()
        df = df.set_index(['Release date'])
        df = df.resample(interval)[column].mean()
        df = pd.DataFrame(df)
        df.reset_index(inplace=True)
        return df

    def apply(self, target_column, function, axis) -> None:
        """ Apply the given function to the dataframe column"""
        df = self.df.df
        df[target_column] = df.apply(function, axis=axis)
        self.df.df = df

    def filter(self, column:str, expression: str):
        """ Filter and change dataframe to have only data that satisfied expression"""
        df = self.df.df
        df = df[eval(f"df['{column}'] {expression}")]
        self.df.df = df

    def search(self, query) -> pd.DataFrame:
        """ Search dataframe based on given query (AppID and Name column) and return dataframe"""
        df = self.df.get_raw().copy()
        result = df[df['AppID'].str.contains(query) | df['Name'].str.contains(query)]
        return result

    def get_correlation(self, x, y) -> float:
        """ Calculate the correlation between 2 columns in dataframe"""
        return self.df.df[x].corr(self.df.df[y])

    def get_image(self, name: str) -> Image:
        df = self.df.get_raw().copy()
        url = df[(df['Name'] == name)]['Header image'].values[0]
        response = requests.get(url)
        return Image.open(BytesIO(response.content))

    def get_specific(self, name: str) -> pd.DataFrame:
        df = self.df.get_raw().copy()
        df = df.loc[df['Name'] == name]
        return df

    def get_saved_name(self) -> list:
        return self.df.get_all_name()

    def add_to_dataframe(self, content: (pd.Series, pd.DataFrame), name: str) -> None:
        """ Add specified content to named dataframe """
        self.df.add_to_saved_df(content, name)

    def get_num_column(self):
        return self.df.get_raw().select_dtypes(include='number').columns.to_list()

    @staticmethod
    def get_non_numeric_columns():
        return ['Estimated owners', 'Windows', 'Mac', 'Linux', 'Genres']
