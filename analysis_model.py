""" Analysis model for all most operation in GUI application
this module handle most of the operation related to the data"""


from io import BytesIO
import webbrowser
import requests
import numpy as np
import pandas as pd
from PIL import Image
from matplotlib.figure import Figure
from dataframesaver import DataFrameSaver as Ds
from matplotlib import pyplot as plt


class Analysis:
    """ Analysis model for all operation in GUI application"""
    def __init__(self, csv_name):
        self.df = Ds(csv_name)

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
        df2 = df.set_index(['Release date'])
        df2 = df2.resample(interval)[column].mean()
        df2 = pd.DataFrame(df2)
        df2.reset_index(inplace=True)
        return df2

    def apply(self, target_column, function, axis) -> None:
        """ Apply the given function to the dataframe column"""
        self.df.df[target_column] = self.df.df.apply(function, axis=axis)

    def filter(self, column: str, expression: str):
        """ Filter and change dataframe to have only data that satisfied expression"""
        df = self.df.df
        df2 = df[eval(f"df['{column}']{expression}")]
        self.df.df = df2

    def filter_str(self, column: str, expression: str):
        """ Filter and change dataframe to have only data that satisfied expression"""
        self.df.df = self.df.df[self.df.df[column].astype(str).str.contains(expression, case=False)]

    def search(self, query) -> pd.DataFrame:
        """ Search dataframe based on given query (AppID and Name column) and return dataframe"""
        df = self.df.get_raw().copy()
        result = df[df['AppID'].str.contains(query, case=False) | df['Name'].str.contains(query, case=False)]
        return result

    def get_correlation(self, x, y) -> float:
        """ Calculate the correlation between 2 columns in dataframe"""
        with np.errstate(invalid='ignore'):
            return self.df.df[x].corr(self.df.df[y])

    def get_image(self, appid: str) -> Image:
        """ Get image from appid (url from dataframe) and return Image object"""
        url = self.get_specific(appid)['Header image'].values[0]
        response = requests.get(url, timeout=2000)
        return Image.open(BytesIO(response.content))

    def get_specific(self, appid: str) -> pd.DataFrame:
        """ Get specific rows in dataframe based on appid and return the dataframe"""
        df = self.df.get_raw().copy()
        df = df.loc[df['AppID'] == str(appid)]
        return df

    @staticmethod
    def plot_histogram(df, x_column: str, x_label: str, y_label: str,
                       title: str = 'Histogram', bins: int = None) -> Figure:
        """ Plot histogram according to input """
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.set_title(title)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        # Remove using SD
        data = df[x_column]
        q1 = data.quantile(0.25)
        q3 = data.quantile(0.75)
        iqr = q3 - q1
        upper_bound = q3 + 1.5 * iqr
        if data.max() < upper_bound:
            upper_bound = data.max()
        lower_bound = q1 - 1.5 * iqr
        if data.min() > lower_bound:
            lower_bound = data.min()
        # plot a graph
        if not bins:
            bins = (upper_bound - lower_bound) / 2
        if bins >= 1:
            plt.hist(df[x_column], bins=bins.__ceil__(), range=(lower_bound, upper_bound))
        else:
            plt.hist(df[x_column], range=(lower_bound, upper_bound))
        return fig

    def plot_scatter(self, df, x_column: str, y_column: str, x_label: str, y_label: str,
                     title: str = 'Scatter Plot') -> Figure:
        """ Plot the scatter plot of the data """
        fig, ax = plt.subplots(figsize=(10, 6))
        plt.scatter(df[x_column], df[y_column])
        corr = self.get_correlation(x_column, y_column)
        ax.set_title(title + f"\n Correlation: {corr:.5f}")
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)

        return fig

    @staticmethod
    def plot_line(df, x_column: str, y_column: str, x_label: str, y_label: str,
                  title: str = 'Line Plot') -> Figure:
        """ Plot the line plot of the data """
        fig, ax = plt.subplots(figsize=(10, 6))
        plt.plot(df[x_column], df[y_column])
        ax.set_title(title)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        return fig

    @staticmethod
    def plot_pie(df, x_column: str,
                 title: str = 'Pie Plot') -> Figure:
        """ Plot the pie plot of the data """

        fig, ax = plt.subplots(figsize=(10, 6))
        n_df = df.groupby(df[x_column]).count().reset_index()

        def assign_others(x):
            """ Combine the values that below 5% of total to "Others"""
            if x['Name'] < 0.015 * n_df['Name'].sum():
                return 'Other'
            return str(x[x_column])

        n_df[x_column] = n_df.apply(assign_others, axis=1)
        n_df = n_df.groupby(n_df[x_column]).sum()
        data = n_df['Name'].to_numpy()
        plt.pie(data, labels=n_df.index, autopct='%1.1f%%')
        ax.set_title(title)
        return fig

    def get_saved_name(self) -> list:
        """ Get all of saved dataframe name"""
        return self.df.get_all_name()

    def get_all_genres(self) -> list:
        """ Get all unique genres of app in the dataframe"""
        df = self.df.get_raw()
        unique = [genre for row in df['Genres'].tolist() for genre in row.split(",")]
        unique = set(unique)
        return list(unique)

    def add_to_dataframe(self, content: (pd.Series, pd.DataFrame), name: str) -> None:
        """ Add specified content to named dataframe """
        self.df.add_to_saved_df(content, name)

    def get_num_column(self):
        """ Get numerical column"""
        return self.df.get_raw().select_dtypes(include='number').columns.to_list()

    @staticmethod
    def get_non_numeric_columns():
        """ Get non-numeric columns (hardcoded)"""
        return ['Estimated owners', 'Windows', 'Mac', 'Linux', 'Genres']

    @staticmethod
    def open_steamdb(appid: str) -> None:
        """ Open steamdb site on user browser"""
        if int(appid) != '':
            webbrowser.open_new(f'https://steamdb.info/app/{appid}')
        else:
            webbrowser.open_new_tab('https://steamdb.info/')

    @staticmethod
    def open_steam(appid: str) -> None:
        """ Open steam site on user browser"""
        if int(appid) != '':
            webbrowser.open_new(f'https://store.steampowered.com/app/{appid}')
        else:
            webbrowser.open_new('https://store.steampowered.com/')
