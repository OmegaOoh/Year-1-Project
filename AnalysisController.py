from Analysis import Analysis

class AnalysisController:
    def __init__(self):
        self.__model = Analysis()

    def get_df(self):
        return self.__model.df.df
