import pandas as pd


class DataFrameSaver:
    def __init__(self, filename:str):
        df = pd.read_csv(filename)
        self.__raw_df = cleanup_df(df)
        self.df = self.__raw_df.copy()
        self.__saved_df = {}

    def save_df(self, name:str):
        """ Saves actives dataframe into a dict"""
        self.__saved_df[name] = self.df.copy()

    def load_df(self, name:str):
        """ Loads dataframe from saved dict by name"""
        if name in self.__saved_df:
            self.df = self.__saved_df[name].copy()
        else:
            raise KeyError(f"{name} does not exist in saved dataframes")

    def reset_df(self):
        """ Resets active dataframe to raw data"""
        self.df = self.__raw_df.copy()


def cleanup_df(df) -> pd.DataFrame:
    """ handle missing data from input dataframe """
    df = df[df['Genres'].notna()]
    df = df[df['Categories'].notna()]
    df = df[df['Publishers'].notna()]
    df = df.dropna(axis=1)
    return df
