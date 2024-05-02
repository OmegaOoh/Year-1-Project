""" GUI module for analysis application"""

import tkinter as tk
from tkinter import ttk, font
from PIL import ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from analysis_controller import AnalysisController


class AnalysisGUI(tk.Tk):
    """ GUI class for analysis application"""
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


        # Single Data Pages Variable
        self.__query = tk.StringVar()
        self.__table = None
        self.__detail_comp = {}

        self.__init_component()

    def __init_component(self):
        """ initialize tkinter component"""
        self.defaultFont = font.nametofont('TkDefaultFont')
        self.defaultFont.configure(size=12)
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
        descriptive_frame = tk.LabelFrame(root, text='Descriptive Statistic', font='32')

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
        corr = self.analysis.get_correlation('Price', 'Rating')
        temp_df = self.analysis.get_df()
        scatter_fig = self.plot_scatter(temp_df, "Price", "Rating"
                                        , "Price", "Rating", f"Scatter of Price and Rating \n"
                                                             f"Correlation: {corr:.5f}")
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
        t = tk.Label(root, text='Explore (Not Implement yet)')
        t.pack(fill=tk.BOTH, expand=True)

    def __init_single_data(self):
        """ Initialise the single data page component"""
        root = self.pages['Single Data']

        # create table view
        table_frame = tk.Frame(root)
        self.__create_table_searchbar(table_frame)
        table_frame.columnconfigure(0, weight=100)
        table_frame.columnconfigure(1, weight=20)
        table_frame.columnconfigure(2, weight=1)
        table_frame.rowconfigure(0, weight=1)
        table_frame.rowconfigure(1, weight=500)
        # create game detail frame
        detail_frame = tk.Frame(root)
        self.__create_detail(detail_frame)
        self.__table.bind('<<TreeviewSelect>>', self.handle_select_game)
        # main layout management
        detail_frame.grid(sticky=tk.NSEW, column=0, row=0)
        self.__detail_comp['detail frame'] = detail_frame
        table_frame.grid(sticky=tk.NSEW, column=1, row=0)
        root.columnconfigure(0, weight=4)
        root.columnconfigure(1, weight=1)
        root.rowconfigure(0, weight=1)

    def __create_detail(self, root):
        """ Create the frame to display the game details """
        picture_frame = tk.Frame(root)
        pic_label = tk.Label(picture_frame)
        pic_label.pack(side=tk.LEFT, padx=5, pady=5, expand=True, fill=tk.BOTH)
        self.__detail_comp['picture'] = pic_label

        picture_frame.bind('<Configure>', lambda x: self.resize_image(pic_label, x))

        # Text element
        title_label = tk.Label(root, text="Title :")
        title = tk.Label(root, font=16)
        self.__detail_comp['game title'] = title

        price_label = tk.Label(root, text="Price :")
        price = tk.Label(root, font=16)
        self.__detail_comp['price'] = price

        publisher_label = tk.Label(root, text="Publishers :")
        pub = tk.Label(root, font=16)
        self.__detail_comp['publisher'] = pub

        genres_label = tk.Label(root, text="Genres :")
        genres = tk.Label(root, font=16)
        self.__detail_comp['genre'] = genres

        peak_ccu_label = tk.Label(root, text="Peak CCU: ")
        peak_ccu = tk.Label(root, font=16)
        self.__detail_comp['peakCCU'] = peak_ccu

        average_playtime_label = tk.Label(root, text="Average Playtime")
        avg_playtime = tk.Label(root, font=16)
        self.__detail_comp['playtime'] = avg_playtime

        positive_label = tk.Label(root, text="Positive: ")
        pos = tk.Label(root)
        self.__detail_comp['positive'] = pos

        negative_label = tk.Label(root, text="Negative: ")
        neg = tk.Label(root)
        self.__detail_comp['negative'] = neg

        add_to_label = tk.Label(root, text="Add to :", font = 16)
        add_combobox = ttk.Combobox(root)
        self.__detail_comp['combobox'] = add_combobox
        add_button = tk.Button(root, text="Add")
        self.__detail_comp['button'] = add_button

        add_button['state'] = tk.DISABLED
        add_button.bind("<Button-1>", self.handle_adds_button)
        add_combobox['state'] = tk.DISABLED

        picture_frame.grid(sticky=tk.NSEW, row=0, column=0, columnspan=2, rowspan=2)
        title_label.grid(sticky=tk.NSEW, row=0, column=2)
        title.grid(sticky=tk.NSEW, row=0, column=3)
        price_label.grid(sticky=tk.NSEW, row=1, column=2)
        price.grid(sticky=tk.NSEW, row=1, column=3)
        publisher_label.grid(sticky=tk.NSEW, row=2, column=0)
        pub.grid(sticky=tk.NSEW, row=2, column=1)
        genres_label.grid(sticky=tk.NSEW, row=2, column=2)
        genres.grid(sticky=tk.NSEW, row=2, column=3)
        peak_ccu_label.grid(sticky=tk.NSEW, row=3, column=0)
        peak_ccu.grid(sticky=tk.NSEW, row=3, column=1)
        average_playtime_label.grid(sticky=tk.NSEW, row=3, column=2)
        avg_playtime.grid(sticky=tk.NSEW, row=3, column=3)
        positive_label.grid(sticky=tk.NSEW, row=4, column=0)
        pos.grid(sticky=tk.NSEW, row=4, column=1)
        negative_label.grid(sticky=tk.NSEW, row=4, column=2)
        neg.grid(sticky=tk.NSEW, row=4, column=3)

        add_to_label.grid(sticky=tk.W, row=5, column=0)
        add_combobox.grid(sticky=tk.EW, row=6, column=1, columnspan=2)
        add_button.grid(sticky=tk.EW, row=6, column=3)

        for i in range(6):
            root.rowconfigure(i, weight=5)
        root.rowconfigure(6, weight=1)
        for i in range(4):
            root.columnconfigure(i, weight=1)

    def __create_table_searchbar(self, root):
        """ Create the search bar and table component that attach to root frame"""
        scroll = tk.Scrollbar(root, orient='vertical')
        self.__table = ttk.Treeview(root, yscrollcommand=scroll.set)
        scroll.configure(command=self.__table.yview)
        self.__table.column('#0', width=0, stretch=tk.NO)
        self.__table.heading('#0', text='', anchor=tk.W)
        self.__table['columns'] = ('AppID', "Name")
        # Define Column
        self.__table.column('AppID', anchor=tk.W, stretch=tk.NO)
        self.__table.column('Name', anchor=tk.W)
        # Define Heading
        self.__table.heading('AppID', text='AppID', anchor=tk.CENTER)
        self.__table.heading('Name', text='Name', anchor=tk.CENTER)
        self.load_table(self.analysis.get_raw())

        # implement search bar
        search_bar = tk.Entry(root, textvariable=self.__query)
        search_bar.bind('<Return>', lambda x: self.handle_search())
        search_button = tk.Button(root, text='Search', font='16', command=self.handle_search)

        # Table and Search bar layout management
        search_bar.grid(sticky=tk.NSEW, column=0, row=0)
        search_button.grid(sticky=tk.NSEW, column=1, row=0, columnspan=2)
        scroll.grid(sticky=tk.NSEW, column=2, row=1)
        self.__table.grid(sticky=tk.NSEW, column=0, row=1, columnspan=2)

    def change_image(self, image_name: str, label: tk.Label) -> None:
        self.__detail_comp['image'] = self.analysis.get_picture(image_name)
        img = ImageTk.PhotoImage(self.__detail_comp['image'])
        label.configure(image=img)
        label.image = img

    def resize_image(self, label: tk.Label, e: tk.Event) -> None:
        """ Resize to image according to width and height of the frame (according to events)"""
        try:
            img = self.__detail_comp['image'].copy()
        except KeyError:
            return
        img = img.copy()
        shape = img.size
        ratio = shape[0] / shape[1]
        w = int(3*e.width/4) + 1
        h = int(w / ratio) + 1
        resized_image = ImageTk.PhotoImage(img.resize((w, h)))
        label.configure(image=resized_image)
        label.image = resized_image

    def handle_select_game(self, *args):
        self.__detail_comp['button']['state'] = tk.NORMAL
        self.__detail_comp['combobox']['state'] = tk.NORMAL

        item_loc = self.__table.focus()
        item = self.__table.item(item_loc)
        try:
            item_name = item['values'][1]
        except IndexError:
            return
        self.change_image(item_name, self.__detail_comp['picture'])
        details = self.analysis.get_specific(item_name)

        def get_detail(column: str) -> str:
            return details[column].values[0]

        self.__detail_comp['selected'] = item_name

        self.__detail_comp['game title'].configure(text=get_detail('Name'))
        self.__detail_comp['price'].configure(text=f'{get_detail('Price'):,.2f} USD')
        self.__detail_comp['publisher'].configure(text=get_detail('Publishers'))
        self.__detail_comp['genre'].configure(text=get_detail('Genres'))
        self.__detail_comp['peakCCU'].configure(text=get_detail('Peak CCU'))
        self.__detail_comp['playtime'].configure(text=f"{get_detail('Average playtime forever'):,}")
        self.__detail_comp['positive'].configure(text=f"{get_detail('Positive'):,}")
        self.__detail_comp['negative'].configure(text=f"{get_detail('Negative'):,}")

        self.load_dataframe_name()

    def handle_adds_button(self, *args):
        df_name = str(self.__detail_comp['combobox'].get())
        if df_name.isspace() or df_name == '':
            df_name = 'untitled'
        print('Name: ', df_name)
        try:
            item_name = self.__detail_comp['selected']
            df = self.analysis.get_specific(item_name)
            self.analysis.add_to_dataframe(df, df_name)
        except KeyError:
            return

    def load_dataframe_name(self):
        combobox = self.__detail_comp['combobox']
        ls = self.analysis.get_dataframes_name()
        combobox['values'] = ls

    def handle_search(self):
        # TODO Long Running Task
        query = self.__query.get()
        self.clear_table()
        if not query.isspace():
            searched_df = self.analysis.search(query)
            self.load_table(searched_df)

    def load_table(self, dataframe):
        # TODO Long Running Task
        self.clear_table()
        df = dataframe.copy()
        df = df[['AppID', 'Name']]
        for i, r in df.iterrows():
            self.__table.insert("", 0, text=i, values=list(r))

    def clear_table(self):
        self.__table.delete(*self.__table.get_children())

    @staticmethod
    def plot_histogram(df, x_column: str, x_label: str, y_label: str,
                       title: str = 'Histogram', bins: int = None) -> Figure:
        """ Plot the histogram of the data """
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.set_title(title)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        # Remove using SD
        data = df[x_column]
        sd = data.std()
        upper_bound = data.mean() + 3*sd
        if data.max() < upper_bound:
            upper_bound = data.max()
        lower_bound = data.mean() - 3*sd
        if data.min() > lower_bound:
            lower_bound = data.min()
        # plot a graph
        if not bins:
            bins = (upper_bound - lower_bound) / 2
        plt.hist(df[x_column], bins=bins.__ceil__(), range=(lower_bound, upper_bound))
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
            return str(x[x_column])

        n_df[x_column] = n_df.apply(assign_others, axis=1)
        n_df = n_df.groupby(n_df[x_column]).sum()
        data = n_df['Name'].to_numpy()
        plt.pie(data, labels=n_df.index, autopct='%1.1f%%')
        ax.set_title(title)
        return fig

    def get_descriptive_statistic(self, root, col: str) -> tk.LabelFrame:
        """ Create a label frame of the descriptive statistics """
        desc = tk.LabelFrame(root, text=col, font="22")
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
        """ Run the application GUI"""
        self.mainloop()
