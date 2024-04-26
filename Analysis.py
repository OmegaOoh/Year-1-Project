import matplotlib.pyplot as plt
from dataframesaver import DataFrameSaver as Ds


class Analysis:
    def __init__(self):
        self.df = Ds('game_market_data.csv')
