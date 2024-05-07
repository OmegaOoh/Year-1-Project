import glob

import pandas as pd
import os


class DataFrameSaver:
    def __init__(self, filename: str):
        self.__raw_df = pd.read_csv(filename)
        self.__raw_df['AppID'] = self.__raw_df['AppID'].astype(str)
        self.df = self.__raw_df.copy(deep=True)
        self.to_datetime()
        self.__raw_df['Release date'] = self.df['Release date']
        self.df = self.__raw_df.copy(deep=True)
        self.__saved_df = {}
        self.read_saved_df()

    def to_datetime(self):
        self.df['Release date'] = self.df['Release date'].apply(lambda x: to_datetime(x))

    def to_list(self, col: str):
        self.df[col] = self.df.apply(lambda x: x[col].split(','), axis=1)

    def save_df(self, name: str):
        """ Saves actives dataframe into a dict"""
        self.__saved_df[name] = self.df.copy()

    def load_df(self, name: str):
        """ Loads dataframe from saved dict by name"""
        if name in self.__saved_df:
            self.df = self.__saved_df[name].copy()
        else:
            raise KeyError(f"{name} does not exist in saved dataframes")

    def reset_df(self):
        """ Resets active dataframe to raw data"""
        self.df = self.__raw_df.copy(deep=True)

    def get_raw(self) -> pd.DataFrame:
        """ Get raw data of the dataset"""
        return self.__raw_df.copy(deep=True)

    def get_all_name(self) -> list:
        """ Get all names of the dataset"""
        return list(self.__saved_df.keys())

    def add_to_saved_df(self, content: (pd.DataFrame, pd.Series), name: str):
        """ Saves dataframe to saved"""
        try:
            df = self.__saved_df[name]
            self.__saved_df[name] = pd.concat([df, content])
            self.__saved_df[name].drop_duplicates(keep='first', inplace=True)
        except KeyError:
            self.__saved_df[name] = pd.DataFrame(content)

    def read_saved_df(self) -> None:
        try:
            os.chdir('saved')
        except FileNotFoundError:
            os.mkdir('saved')
            os.chdir('saved')
        all_csv = glob.glob('*.csv')
        for i in all_csv:
            df = pd.read_csv(i)
            name = str(i).removesuffix('.csv')
            self.__saved_df[name] = df
        os.chdir('../')

    def save_all_df(self):
        try:
            os.chdir('saved')
        except FileNotFoundError:
            os.mkdir('saved')
            os.chdir('saved')
        for i in self.__saved_df:
            self.__saved_df[i].to_csv(i + '.csv')
        os.chdir('../')


def to_datetime(date_str):
    try:
        date_str = pd.to_datetime(date_str, format="%b %d, %Y")
    except ValueError:
        pass
    date_obj = pd.to_datetime(date_str, format="%b %Y")
    return date_obj

