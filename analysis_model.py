import matplotlib.pyplot as plt
import pandas as pd
from dataframesaver import DataFrameSaver as Ds


class Analysis:
    def __init__(self):
        self.df = Ds('game_market_data.csv')

    def to_timeseries_count(self, interval: str) -> pd.DataFrame:
        df = self.df.df.copy()
        df = df.set_index(['Release date'])
        df = df.resample(interval)['Name'].count()
        df = pd.DataFrame(df)
        df.reset_index(inplace=True)
        return df

    def to_timeseries_mean(self, interval: str, column: str) -> pd.DataFrame:
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

    def filter(self, column:str, expression:str):
        df = self.df.df
        df = df[eval(f"df['{column}'] {expression}")]
        self.df.df = df
