import pandas as pd
from pandas.core.interchange import column


class DataFrameSaver:
    def __init__(self, filename: str):
        self.__raw_df = pd.read_csv(filename)
        self.__raw_df['AppID'] = self.__raw_df['AppID'].astype(str)
        self.df = self.__raw_df.copy()
        self.__saved_df = {}

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
        self.df = self.__raw_df.copy()

    def get_raw(self) -> pd.DataFrame:
        """ Get raw data of the dataset"""
        return self.__raw_df

def to_datetime(date_str):
    try:
        date_str = pd.to_datetime(date_str, format="%b %d, %Y")
    except ValueError:
        pass
    date_obj = pd.to_datetime(date_str, format="%b %Y")
    return date_obj
