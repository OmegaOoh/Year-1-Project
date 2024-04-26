import tkinter as tk
from tkinter import ttk

import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from AnalysisController import AnalysisController
import matplotlib.pyplot as plt


class AnalysisGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        # Controller
        self.analysis = AnalysisController()

        # GUI
        self.title('Steam Game Market Analysis')
        self.notebook = ttk.Notebook(self)
        page_name = ['Information', 'Explore', 'Single Data']
        self.pages = {}
        for i in page_name:
            temp = tk.Frame(self.notebook)
            self.pages[i] = temp
        self.__init_component()

    def __init_component(self):
        """ initialize tkinter component"""
        self.__init_information()
        self.__init_explore()
        self.__init_single_data()
        for i in self.pages:
            page = self.pages[i]
            page.pack(fill=tk.BOTH, expand=True)
            self.notebook.add(page, text=i)
        self.notebook.pack(fill=tk.BOTH, expand=True)

    def __init_information(self):
        """ Initialise the information page component"""
        root = self.pages['Information']

        # Distribution of Games Price
        price_fig = self.plot_histogram(self.analysis.get_df(), 'Price',
                                        'Price', 'Number of video games',
                                        'Distribution of Video Games Prices')
        dist_price_cv = FigureCanvasTkAgg(price_fig, root)
        dist_price_cv.draw()
        dist_price_cv.get_tk_widget().grid(sticky=tk.NSEW, column=0, row=0)
        # Game release each year
        temp_df = self.analysis.get_df()
        temp_df['Release date'] = temp_df['Release date'].apply(lambda x: to_datetime_(x))
        temp_df = temp_df.set_index(['Release date'])
        temp_df = temp_df.resample('YE')['Name'].count()
        temp_df = pd.DataFrame(temp_df)
        temp_df = temp_df.reset_index()
        price_y_fig = self.plot_line(temp_df, "Release date", "Name",
                                     'Release Date', "Number of Video Games", "Game release each Year")
        price_y_cv = FigureCanvasTkAgg(price_y_fig, root)
        price_y_cv.draw()
        price_y_cv.get_tk_widget().grid(sticky=tk.NSEW, column=1, row=0)

        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        root.columnconfigure(1, weight=1)
        root.rowconfigure(1, weight=1)
        root.columnconfigure(2, weight=1)

    def __init_explore(self):
        """ Initialise the explore page component"""
        root = self.pages['Explore']
        t = tk.Label(root, text='Explore')
        t.pack(fill=tk.BOTH, expand=True)

    def __init_single_data(self):
        """ Initialise the single data page component"""
        root = self.pages['Single Data']
        t = tk.Label(root, text='Single Data')
        t.pack(fill=tk.BOTH, expand=True)

    @staticmethod
    def plot_histogram(df, x_column: str, x_label: str, y_label: str,
                       title: str = 'Histogram') -> Figure:
        """ Plot the histogram of the data """
        fig, ax = plt.subplots(figsize=(10, 6))
        plt.hist(df[x_column], bins=20, label=x_label)
        ax.set_title(title)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.set_xbound(0)
        return fig

    @staticmethod
    def plot_scatter(df, x_column: str, y_column: str, x_label: str, y_label: str,
                     title: str = 'Scatter Plot') -> Figure:
        """ Plot the scatter plot of the data """
        pass

    @staticmethod
    def plot_bar(df, x_column: str, y_column: str, x_label: str, y_label: str,
                 title: str = 'Bar Plot') -> Figure:
        """ Plot the bar plot of the data """
        pass

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
    def plot_pie(df, attributes: str, x_label: str,
                 title: str = 'Scatter Plot') -> FigureCanvasTkAgg:
        """ Plot the pie plot of the data """
        fig, ax = plt.subplots(figsize=(10, 6))
        plt.pie(df[attributes], labels=attributes, autopct='%1.1f%%',)
        return fig

    def run(self):
        self.mainloop()


def to_datetime_(date_str):
    try:
        date_str = pd.to_datetime(date_str, format="%b %d, %Y")
    except ValueError:
        pass
    date_obj = pd.to_datetime(date_str, format="%b %Y")
    return date_obj
