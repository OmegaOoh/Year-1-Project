import pandas as pd
import dataframesaver as dp
from AnalysisGUI import AnalysisGUI

x = dp.DataFrameSaver('game_market_data.csv')
gui = AnalysisGUI()
gui.run()