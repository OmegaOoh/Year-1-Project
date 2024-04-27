import tkinter as tk
from tkinter import ttk

import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from analysis_controller import AnalysisController
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
        # TODO Handle long running task
        """ Initialise the information page component"""
        root = self.pages['Information']
        descriptive_frame = tk.LabelFrame(root, text='Descriptive Statistic')

        # Distribution of Games Price (histogram)
        price_fig = self.plot_histogram(self.analysis.get_df(), 'Price',
                                        'Price', 'Number of video games',
                                        'Distribution of Video Games Prices')
        dist_price_cv = FigureCanvasTkAgg(price_fig, root)
        dist_price_cv.draw()
        dist_price_cv.get_tk_widget().grid(sticky=tk.NSEW, column=0, row=0)

        # Descriptive Statistic of Rating
        price_desc = self.get_descriptive_statistic(descriptive_frame, 'Price')
        price_desc.grid(sticky=tk.NSEW, column=0, row=0)

        # Game release each year (line graph)
        self.analysis.to_datetime()
        temp_df = self.analysis.count_time('YE')
        price_y_fig = self.plot_line(temp_df, "Release date", "Name",
                                     'Release Date', "Number of Video Games", "Game release each Year")
        price_y_cv = FigureCanvasTkAgg(price_y_fig, root)
        price_y_cv.draw()
        price_y_cv.get_tk_widget().grid(sticky=tk.NSEW, column=1, row=0)

        # Scatter plot of Price and Rating (Scatter)
        self.analysis.reset_df()
        self.analysis.filter('Positive', '!= 0')
        self.analysis.filter('Negative', '!= 0')
        self.analysis.apply('Rating', lambda x: x['Positive'] / (x['Positive'] + x['Negative']) * 100,
                            axis=1)
        temp_df = self.analysis.get_df()
        scatter_fig = self.plot_scatter(temp_df, "Price", "Rating"
                                        , "Price", "Rating", "Scatter of Price and Rating")
        scatter_cv = FigureCanvasTkAgg(scatter_fig, root)
        scatter_cv.draw()
        scatter_cv.get_tk_widget().grid(sticky=tk.NSEW, column=2, row=0)

        # Rating Dist
        rate_dist_fig = self.plot_histogram(self.analysis.get_df(), 'Rating', 'Rating',
                                            'Number of Video Game', 'Distribution of Game Rating')
        rate_dist_cv = FigureCanvasTkAgg(rate_dist_fig, root)
        rate_dist_cv.draw()
        rate_dist_cv.get_tk_widget().grid(sticky=tk.NSEW, column=1, row=1)

        # Descriptive Statistic of Rating
        rating_desc = self.get_descriptive_statistic(descriptive_frame, "Rating")
        rating_desc.grid(sticky=tk.NSEW, column=1, row=0)

        # Ratio of Game Genres (Pie Charts)
        self.analysis.reset_df()
        self.analysis.to_list('Genres')
        self.analysis.apply('Primary Genres', lambda x: x['Genres'][0], axis=1)

        pie_fig = self.plot_pie(self.analysis.get_df(), "Primary Genres",
                                "Ratio of each primary genres")
        pie_cv = FigureCanvasTkAgg(pie_fig, root)
        pie_cv.draw()
        pie_cv.get_tk_widget().grid(sticky=tk.NSEW, column=0, row=1)

        descriptive_frame.grid(sticky=tk.NSEW, column=2, row=1)
        descriptive_frame.columnconfigure(0, weight=1)
        descriptive_frame.columnconfigure(1, weight=1)
        descriptive_frame.rowconfigure(0, weight=1)


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
        fig, ax = plt.subplots(figsize=(10, 6))
        plt.scatter(df[x_column], df[y_column])
        ax.set_title(title)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        return fig

    @staticmethod
    def plot_bar(df, x_column: str, y_column: str, x_label: str, y_label: str,
                 title: str = 'Bar Plot') -> Figure:
        """ Plot the bar plot of the data """
        fig, ax = plt.subplots(figsize=(10, 6))
        n_df = df[[x_column, y_column]]
        n_df = n_df.groupby(x_column).mean()
        plt.bar(n_df.index, n_df[y_column])
        ax.set_title(title)
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
            else:
                return str(x[x_column])

        n_df[x_column] = n_df.apply(assign_others, axis=1)
        n_df = n_df.groupby(n_df[x_column]).sum()
        data = n_df['Name'].to_numpy()
        plt.pie(data, labels=n_df.index, autopct='%1.1f%%')
        ax.set_title(title)
        return fig

    def get_descriptive_statistic(self, root, col: str) -> tk.LabelFrame:
        """ Create a label frame of the descriptive statistics """
        desc = tk.LabelFrame(root, text=col)
        df = self.analysis.get_df()
        range_l = tk.Label(desc, text=f"Range: {df[col].min():.2f} - "
                                      f"{df[col].max():.2f}"
                           , font='16', anchor='w', justify='left')
        mean = tk.Label(desc, text=f"Mean: {df[col].mean():.2f}"
                        , font='16', anchor='w', justify='left')
        median = tk.Label(desc, text=f"Median: {df[col].median():.2f}"
                          , font='16', anchor='w', justify='left')
        mode_val = df[col].mode()
        count_mode_val = df[df[col] == mode_val[0]].count()[col]
        mode = tk.Label(desc, text=f"Mode: {mode_val[0]}, Count: {count_mode_val}"
                        , font='16', anchor='w', justify='left')
        sd = tk.Label(desc, text=f"SD: {df[col].std():.2f}", font='16', anchor='w', justify='left')
        var = tk.Label(desc, text=f"Variance: {df[col].var():.2f}"
                       , font='16', anchor='w', justify='left')
        q1 = df[col].quantile(0.25)
        q1_l = tk.Label(desc, text=f"Q1: {q1:.2f}", font='16', anchor='w', justify='left')
        q3 = df[col].quantile(0.75)
        q3_l = tk.Label(desc, text=f"Q1: {q3:.2f}", font='16', anchor='w', justify='left')
        iqr = q3-q1
        iqr_l = tk.Label(desc, text=f"IQR: {iqr:.2f}", font='16', anchor='w', justify='left')

        extendable = {'expand': True, 'fill': tk.X}
        range_l.pack(side=tk.TOP, **extendable)
        mean.pack(side=tk.TOP, **extendable)
        median.pack(side=tk.TOP, **extendable)
        mode.pack(side=tk.TOP, **extendable)
        sd.pack(side=tk.TOP, **extendable)
        var.pack(side=tk.TOP, **extendable)
        q1_l.pack(side=tk.TOP, **extendable)
        q3_l.pack(side=tk.TOP, **extendable)
        iqr_l.pack(side=tk.TOP, **extendable)
        return desc

    def run(self):
        self.mainloop()
