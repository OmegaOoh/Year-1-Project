""" GUI module for analysis application"""

import threading
from queue import Queue
import tkinter as tk
import tkinter.messagebox
from tkinter import ttk, font
from PIL import ImageTk
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from analysis_controller import AnalysisController
plt.switch_backend('tkAgg')


class AnalysisGUI(tk.Tk):
    """ GUI class for analysis application"""

    def __init__(self):
        super().__init__()
        # Controller
        self.analysis = AnalysisController()
        # Main GUI
        self.title('Steam Game Market Analysis')
        self.notebook = ttk.Notebook(self)
        page_name = ['Information', 'Explore', 'Single Data']
        self.pages = {}
        for i in page_name:
            temp = tk.Frame(self.notebook)
            self.pages[i] = temp

        # Explore Pages Variable
        self.__explore_comp = {}

        # Single Data Pages Variable
        self.__query = tk.StringVar()
        self.__table = None
        self.__detail_comp = {}

        self.__init_component()

    def __init_component(self):
        """ initialize tkinter component"""

        self.defaultFont = font.nametofont('TkDefaultFont')
        self.defaultFont.configure(size=12)

        self.__init_explore()
        self.__init_single_data()
        self.__init_information()

        for i in self.pages:
            page = self.pages[i]
            page.pack(fill=tk.BOTH, expand=True)
            self.notebook.add(page, text=i)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self.notebook.bind('<<NotebookTabChanged>>', self.handle_tab_change)

        # Set initial screen size to prevent the window to be larger than screen
        width = self.winfo_screenwidth()
        height = self.winfo_screenheight()
        self.geometry(f'{int(0.75 * width)}x{int(0.75 * height)}')

        menubar = tk.Menu(self)
        self.config(menu=menubar)
        file_menu = tk.Menu(menubar)
        file_menu.add_command(label='Save', command=self.analysis.save_all)
        file_menu.add_command(label='Exit', command=self.exit)
        menubar.add_cascade(label='File', menu=file_menu)

        self.protocol('WM_DELETE_WINDOW', self.exit)

    def __init_information(self):
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
        def filter_df():
            self.analysis.reset_df()
            self.analysis.filter('Positive', '!= 0')
            self.analysis.filter('Negative', '!= 0')
            self.analysis.apply('Rating', lambda x: x['Positive'] / (x['Positive'] + x['Negative']) * 100,
                                axis=1)

        def filter_data():
            progress_bar = ttk.Progressbar(root, orient=tk.VERTICAL, mode='indeterminate')
            progress_bar.grid(sticky=tk.NSEW, row=2, column=0)
            thread = threading.Thread(target=filter_df)
            thread.start()
            progress_bar.start()
            while thread.is_alive():
                self.update()
            progress_bar.stop()
            progress_bar.grid_forget()

        filter_data()
        temp_df = self.analysis.get_df()
        scatter_fig = self.plot_scatter(temp_df, "Price", "Rating",
                                        "Price", "Rating", f"Scatter of Price and Rating")
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
        def filter_df2():
            self.analysis.reset_df()
            self.analysis.to_list('Genres')
            self.analysis.apply('Primary Genres', lambda x: x['Genres'][0], axis=1)

        def filter_data():
            progress_bar = ttk.Progressbar(root, orient=tk.VERTICAL, mode='indeterminate')
            progress_bar.grid(sticky=tk.NSEW, row=0, column=1)
            thread = threading.Thread(target=filter_df2)
            thread.start()
            progress_bar.start()
            while thread.is_alive():
                self.update()
            progress_bar.stop()
            progress_bar.grid_forget()

        filter_data()

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
        filter_area = tk.LabelFrame(root, text="Filter")
        dataframe_combobox = ttk.Combobox(filter_area)
        self.load_dataframe_name(dataframe_combobox)
        dataframe_combobox['values'] = ['full']
        dataframe_combobox.current(0)
        dataframe_combobox['state'] = 'readonly'
        self.__explore_comp['df'] = dataframe_combobox
        dataframe_combobox.grid(sticky=tk.EW, padx=5, pady=5, column=0, row=0)

        filter_data = tk.LabelFrame(filter_area, text="Data filter Condition")
        cond_cbb1 = ttk.Combobox(filter_data, state='readonly')
        col_list = []
        for i in self.analysis.get_filter_columns().values():
            col_list += i
        cond_cbb1['values'] = col_list
        cond_cbb1.current(0)
        cond_cbb2 = ttk.Combobox(filter_data, state='readonly')
        cond_cbb3 = ttk.Combobox(filter_data, state=tk.NORMAL)
        add_button = ttk.Button(filter_data, text="Add Filter")

        tree_view = ttk.Treeview(filter_data)

        tree_view.column('#0', width=0, stretch=tk.NO)
        tree_view.heading('#0', text='', anchor=tk.W)

        tree_view['columns'] = ('Data Column', "Condition", "Values")
        tree_view.heading(column=0, text="Data Column")
        tree_view.heading(column=1, text="Condition")
        tree_view.heading(column=2, text="Values")

        tree_view.column('Data Column', anchor=tk.W)
        tree_view.column('Condition', anchor=tk.W)
        tree_view.column('Values', anchor=tk.W)

        def add_filter():
            try:
                data = cond_cbb1.get()
                cond = cond_cbb2.get()
                val = cond_cbb3.get()
                temp = [data, cond, val]
                tree_view.insert("", tk.END, values=temp)
            except tkinter.TclError:
                return

        def remove_filter():
            try:
                tree_view.delete(tree_view.selection()[0])
            except IndexError:
                return

        remove_filter_button = ttk.Button(filter_data, text="Remove Filter", command=lambda: remove_filter())

        self.__explore_comp['condition1'] = cond_cbb2
        self.__explore_comp['condition2'] = cond_cbb3
        cond_cbb1.bind('<<ComboboxSelected>>', self.handle_filter_change)
        add_button.bind("<Button-1>", lambda x: add_filter())

        cond_cbb1.grid(sticky=tk.NSEW, padx=5, pady=5, column=0, row=0)
        cond_cbb2.grid(sticky=tk.NSEW, padx=5, pady=5, column=1, row=0)
        cond_cbb3.grid(sticky=tk.NSEW, padx=5, pady=5, column=2, row=0)
        add_button.grid(sticky=tk.NSEW, padx=5, pady=5, column=2, row=1)
        tree_view.grid(sticky=tk.NSEW, padx=5, pady=5, column=0, row=2, columnspan=3)
        remove_filter_button.grid(sticky=tk.NSEW, padx=5, pady=5, column=2, row=3)

        data_frame = ttk.LabelFrame(filter_area, text='Plot')

        data1_label = ttk.Label(data_frame, text='X')
        data1 = ttk.Combobox(data_frame, state='readonly')
        self.__explore_comp['data1'] = data1
        data2_label = ttk.Label(data_frame, text='Y')
        data2 = ttk.Combobox(data_frame, state='readonly')
        self.__explore_comp['data2'] = data2
        graph_label = tk.Label(data_frame, text='Graph Type: ')
        graph_type = ttk.Combobox(data_frame, state='readonly')
        graph_type['values'] = ['Scatter', 'Histogram', 'Pie', 'Line']
        graph_type.current(0)
        graph_type.bind('<<ComboboxSelected>>', self.handle_change_graph_type)

        # Set initial combobox values
        self.select_filter(cond_cbb1.get())
        self.select_graph_type(graph_type.get())

        def extract_tree():
            ls = []
            for line in tree_view.get_children():
                t = ""
                for value in tree_view.item(line)["values"]:
                    t += str(value).replace(' ', '_') + ' '
                t.strip()
                ls.append(t)
            return ls

        visualize_button = ttk.Button(data_frame, text='Visualize',
                                      command=lambda: self.handle_visualize(data1.get(),
                                                                            data2.get(),
                                                                            graph_type.get(),
                                                                            extract_tree()))
        data1_label.grid(sticky=tk.NSEW, padx=5, pady=5, column=0, row=0)
        data1.grid(sticky=tk.NSEW, padx=5, pady=5, column=1, row=0)
        data2_label.grid(sticky=tk.NSEW, padx=5, pady=5, column=2, row=0)
        data2.grid(sticky=tk.NSEW, padx=5, pady=5, column=3, row=0)
        graph_label.grid(sticky=tk.NSEW, padx=5, pady=5, column=0, row=1)
        graph_type.grid(sticky=tk.NSEW, padx=5, pady=5, column=1, row=1)
        visualize_button.grid(sticky=tk.NSEW, padx=5, pady=5, column=3, row=2)

        data_frame.columnconfigure(0, weight=1)
        data_frame.columnconfigure(1, weight=1)
        data_frame.columnconfigure(2, weight=1)
        data_frame.columnconfigure(3, weight=1)
        data_frame.rowconfigure(0, weight=1)
        data_frame.rowconfigure(1, weight=1)
        data_frame.rowconfigure(2, weight=1)

        for i in range(3):
            filter_data.columnconfigure(i, weight=1)
        filter_data.rowconfigure(2, weight=10)

        filter_data.grid(sticky=tk.NSEW, padx=5, pady=5, column=0, row=1, columnspan=2)
        data_frame.grid(sticky=tk.NSEW, padx=5, pady=5, column=0, row=2, columnspan=2)

        filter_area.grid(sticky=tk.NSEW, padx=5, pady=5, column=1, row=0)

        filter_area.rowconfigure(1, weight=10)
        filter_area.rowconfigure(2, weight=1)
        filter_area.columnconfigure(0, weight=1)
        filter_area.columnconfigure(1, weight=5)

        plot_area = tk.LabelFrame(root, text='Plot', padx=5, pady=5)

        self.__explore_comp['plot'] = plot_area

        plot_area.grid(sticky=tk.NSEW, row=0, column=0)
        plot_area.columnconfigure(0, weight=1)
        plot_area.rowconfigure(0, weight=1)

        root.columnconfigure(0, weight=1)
        root.columnconfigure(1, weight=1)
        root.rowconfigure(0, weight=1)

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

    def handle_change_graph_type(self, e: tk.Event) -> None:
        selected = e.widget.get()
        self.select_graph_type(selected)

    def select_graph_type(self, selected):
        match selected:
            case 'Histogram':
                self.__explore_comp['data1']['value'] = self.analysis.get_num_column()
                self.__explore_comp['data2']['state'] = tk.DISABLED
            case "Scatter":
                self.__explore_comp['data1']['value'] = self.analysis.get_num_column()
                self.__explore_comp['data2']['state'] = 'readonly'
                self.__explore_comp['data2']['value'] = self.analysis.get_num_column()
                self.__explore_comp['data1']['value'] = self.analysis.get_num_column()
                self.__explore_comp['data2'].current(0)
            case "Pie":
                self.__explore_comp['data1']['value'] = self.analysis.get_non_numeric_columns()
                self.__explore_comp['data2']['state'] = tk.DISABLED
            case "Line":
                self.__explore_comp['data1']['value'] = ['count', 'average']
                self.__explore_comp['data2']['value'] = self.analysis.get_num_column()
                self.__explore_comp['data2']['state'] = 'readonly'
                self.__explore_comp['data2'].current(0)
        self.__explore_comp['data1'].current(0)

    def handle_visualize(self, x: str = 'Price', y: str = 'Positive',
                         graph_type: str = 'Histogram', filter_list: list = None):
        try:
            fig = self.__explore_comp['figure']
            fig.get_tk_widget().grid_forget()
            plt.close(fig.figure)
            del fig
        except KeyError:
            pass
        try:
            self.analysis.load_df(self.__explore_comp['df'].get())
        except KeyError:
            self.analysis.reset_df()

        root = self.__explore_comp['plot']

        def filter_df():
            for i in filter_list:
                i = i.split(' ')
                expression = i[1] + " " + i[2].replace('_', ' ')
                if i[1] == 'contains':
                    self.analysis.filter_str(i[0], str(i[2].replace('_', ' ')))
                else:
                    self.analysis.filter(i[0].replace('_', ' '), expression)

        def filter_data():
            progress_bar = ttk.Progressbar(root, orient=tk.VERTICAL,
                                           mode='indeterminate')
            progress_bar.grid(sticky=tk.NSEW, row=0, column=0)
            thread = threading.Thread(target=filter_df)
            thread.start()
            progress_bar.start()
            while thread.is_alive():
                self.update()
            progress_bar.stop()
            progress_bar.grid_forget()

        filter_data()

        df = self.analysis.get_df()
        match graph_type:
            case 'Histogram':
                plot = self.plot_histogram(df, x, x, '')
            case "Scatter":
                if x == y:
                    tk.messagebox.showinfo("Invalid XY", "X and Y must be different")
                    return
                plot = self.plot_scatter(df, x, y, x, y)
            case "Pie":
                plot = self.plot_pie(df, x)
            case "Line":
                x_col = 'Release date'
                if x == 'count':
                    df = self.analysis.count_time()
                    plot = self.plot_line(df, x_col, 'Name', x_col, y)
                elif x == 'average':
                    df = self.analysis.mean_time(y)
                    plot = self.plot_line(df, x_col, y, x_col, y)
        figure = FigureCanvasTkAgg(plot, root)
        figure.draw()
        figure.get_tk_widget().grid(sticky=tk.NSEW, column=0, row=0)
        self.__explore_comp['figure'] = figure

    def handle_tab_change(self, event: tk.Event):
        i = self.notebook.index(self.notebook.select())
        if i == 1:
            # Update dataframe combobox each time the user select the explore tabs
            combobox = self.__explore_comp['df']
            self.load_dataframe_name(combobox)
            combobox['values'] = ['full'] + list(combobox['values'])

    def handle_filter_change(self, event: tk.Event):
        widget = event.widget
        selected = widget.get()
        self.select_filter(selected)

    def select_filter(self, selected):
        self.analysis.reset_df()
        full_dict = self.analysis.get_filter_columns()
        cbb = self.__explore_comp['condition1']
        cbb['values'] = []
        if selected in full_dict['num']:
            cbb = self.__explore_comp['condition1']
            cbb['values'] = ['<=', '>=', '<', '>', '==', '!=']
            cbb.current(0)
            cbb = self.__explore_comp['condition2']
            cbb['values'] = self.analysis.get_df()[selected].unique().tolist()
            cbb['state'] = tk.NORMAL
            cbb.current(0)
        if selected in full_dict['other']:
            cbb = self.__explore_comp['condition1']
            cbb['values'] = ['contains']
            if selected == 'Genres':
                cbb.current(0)
                q = Queue()

                def get_genres():
                    g = self.analysis.get_unique_genres()
                    q.put(g)

                thread = threading.Thread(target=get_genres)
                thread.start()
                progressbar = ttk.Progressbar(self, orient=tk.VERTICAL, mode='indeterminate')
                progressbar.pack(side=tk.TOP, fill=tk.X, expand=True)
                progressbar.start()

                def wait():
                    if not thread.is_alive():
                        return
                    self.update()
                    self.after(10, wait)

                wait()
                progressbar.stop()
                progressbar.pack_forget()
                thread.join()
                cbb = self.__explore_comp['condition2']
                cbb['values'] = q.get()
                cbb.current(0)
            else:
                cbb.current(0)
                cbb = self.__explore_comp['condition2']
                cbb['values'] = self.analysis.get_df()[selected].unique().tolist()
            if selected != 'Genres' or selected != 'Publisher':
                cbb['state'] = 'readonly'
            else:
                cbb['state'] = tk.NORMAL
            cbb.current(0)

    def __create_detail(self, root):
        """ Create the frame to display the game details """
        picture_frame = tk.Frame(root)
        pic_label = tk.Label(picture_frame)
        pic_label.pack(side=tk.LEFT, padx=5, pady=5, expand=True, fill=tk.BOTH)
        self.__detail_comp['picture'] = pic_label

        picture_frame.bind('<Configure>', lambda x: self.resize_image(pic_label, x))

        # Text element
        title_label = tk.Label(root, text="Title :")
        title = tk.Label(root)
        self.__detail_comp['game title'] = title

        price_label = tk.Label(root, text="Price :")
        price = tk.Label(root)
        self.__detail_comp['price'] = price

        publisher_label = tk.Label(root, text="Publishers :")
        pub = tk.Label(root)
        self.__detail_comp['publisher'] = pub

        genres_label = tk.Label(root, text="Genres :")
        genres = tk.Label(root)
        self.__detail_comp['genre'] = genres

        peak_ccu_label = tk.Label(root, text="Peak CCU: ")
        peak_ccu = tk.Label(root)
        self.__detail_comp['peakCCU'] = peak_ccu

        average_playtime_label = tk.Label(root, text="Average Playtime")
        avg_playtime = tk.Label(root)
        self.__detail_comp['playtime'] = avg_playtime

        positive_label = tk.Label(root, text="Positive: ")
        pos = tk.Label(root)
        self.__detail_comp['positive'] = pos

        negative_label = tk.Label(root, text="Negative: ")
        neg = tk.Label(root)
        self.__detail_comp['negative'] = neg

        est_own_label = tk.Label(root, text="Estimated Owner :")
        est_own = tk.Label(root)
        self.__detail_comp['est_owner'] = est_own

        steamdb = tk.Label(root, text="Visit Steamdb Site", fg='blue', cursor='hand2')
        steamdb.bind("<Button-1>", lambda x: self.analysis.visit_steamdb())
        self.__detail_comp['steamdb'] = steamdb

        steam = tk.Label(root, text="Visit Steam Store", fg='blue', cursor='hand2')
        steam.bind("<Button-1>",lambda x: self.analysis.visit_steam())
        self.__detail_comp['steam'] = steam

        add_to_label = tk.Label(root, text="Add to :")
        add_combobox = ttk.Combobox(root)
        self.__detail_comp['combobox'] = add_combobox
        add_button = ttk.Button(root, text="Add")
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
        est_own_label.grid(sticky=tk.NSEW, row=5, column=0)
        est_own.grid(sticky=tk.NSEW, row=5, column=1)
        steamdb.grid(sticky=tk.NSEW, row=5, column=2)
        steam.grid(sticky=tk.NSEW, row=5, column=3)

        add_to_label.grid(sticky=tk.W, row=6, column=0)
        add_combobox.grid(sticky=tk.EW, row=7, column=1, columnspan=2)
        add_button.grid(sticky=tk.EW, row=7, column=3)

        for i in range(7):
            root.rowconfigure(i, weight=5)
        root.rowconfigure(7, weight=1)
        for i in range(5):
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

        q = Queue()

        try:
            old_image = label.image  # Save the copy of the image to prevent from python garbage collection
        except AttributeError:
            old_image = None
        label.configure(image=None)
        label.image = None

        def load_img():
            image = self.analysis.get_picture(image_name)
            q.put(image)

        thread = threading.Thread(target=load_img)
        thread.start()

        def wait_process(i):
            ls = ['...', '..', '.']
            if not thread.is_alive():
                return
            label.configure(text='Loading' + ls[i])
            self.update()
            i += 1
            if i > 2:
                i = 0
            self.after(100, lambda: wait_process(i))

        wait_process(0)
        label.configure(text='')
        self.__detail_comp['image'] = q.get()
        img = ImageTk.PhotoImage(self.__detail_comp['image'])
        label.configure(image=img)
        label.image = img
        if old_image:
            del old_image

    def resize_image(self, label: tk.Label, e: tk.Event) -> None:
        """ Resize to image according to width and height of the frame (according to events)"""
        try:
            if self.__detail_comp['image'] is not None:
                img = self.__detail_comp['image']
            else:
                return
        except KeyError:
            return

        shape = img.size
        ratio = shape[0] / shape[1]
        w = int(3 * e.width / 4) + 1
        h = int(w / ratio) + 1
        resized = img.resize((w, h))
        resized_imgtk = ImageTk.PhotoImage(resized)
        label.configure(image=resized_imgtk)
        label.image = resized_imgtk
        self.__detail_comp['image'] = resized

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
        self.__detail_comp['price'].configure(text=f'{get_detail("Price"):,.2f} USD')
        self.__detail_comp['publisher'].configure(text=get_detail('Publishers'))
        self.__detail_comp['genre'].configure(text=get_detail('Genres'))
        self.__detail_comp['peakCCU'].configure(text=get_detail('Peak CCU'))
        self.__detail_comp['playtime'].configure(text=f"{get_detail('Average playtime forever'):,}")
        self.__detail_comp['positive'].configure(text=f"{get_detail('Positive'):,}")
        self.__detail_comp['negative'].configure(text=f"{get_detail('Negative'):,}")
        self.__detail_comp['est_owner'].configure(text=get_detail('Estimated owners'))
        self.__detail_comp['steam'].unbind('<Button-1>')
        self.__detail_comp['steamdb'].unbind('<Button-1>')
        self.__detail_comp['steam'].bind("<Button-1>", lambda x: self.analysis.visit_steam(get_detail('Name')))
        self.__detail_comp['steamdb'].bind("<Button-1>", lambda x: self.analysis.visit_steamdb(get_detail('Name')))

        self.load_dataframe_name(self.__detail_comp['combobox'])

    def handle_adds_button(self, *args):
        df_name = str(self.__detail_comp['combobox'].get())
        if df_name.isspace() or df_name == '' or df_name == 'full':
            tkinter.messagebox.showinfo('Warning', 'Dataframe name does not allowed, saved to untitled dataframe.')
            df_name = 'untitled'
        try:
            item_name = self.__detail_comp['selected']
            df = self.analysis.get_specific(item_name)
            self.analysis.add_to_dataframe(df, df_name)
        except KeyError:
            return

    def load_dataframe_name(self, combobox):
        ls = self.analysis.get_dataframes_name()
        combobox['values'] = ls

    def handle_search(self):
        search_q = self.__query.get()
        if not search_q.isspace() and search_q != '':
            q = Queue()

            self.clear_table()

            def search(query: str, queue: Queue):
                r = self.analysis.search(query)
                queue.put(r)

            def wait():
                if not thread.is_alive():
                    return
                self.after(10, wait)

            thread = threading.Thread(target=lambda: search(search_q, q))
            thread.start()

            wait()
            thread.join()
            self.load_table(q.get())

    def load_table(self, dataframe):
        q = Queue()

        def data_prep(df, que: Queue):
            df = df[['AppID', 'Name']]
            for i, r in df.iterrows():
                data = (i, list(r))
                que.put(data)

        thread = threading.Thread(target=data_prep, args=(dataframe, q))
        thread.start()
        self.clear_table()

        def update_table():
            if not q.empty():
                for _ in range(1000):
                    if q.empty():
                        break
                    index, values = q.get()
                    self.__table.insert("", 0, text=index, values=values)
                self.update()
                self.after(1, update_table)

        thread.join()
        update_table()

    def clear_table(self):
        self.__table.delete(*self.__table.get_children())

    @staticmethod
    def plot_histogram(df, x_column: str, x_label: str, y_label: str,
                       title: str = 'Histogram', bins: int = None) -> Figure:
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
        corr = self.analysis.get_correlation(x_column, y_column)
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

    def get_descriptive_statistic(self, root, col: str) -> tk.LabelFrame:
        """ Create a label frame of the descriptive statistics """
        desc = tk.LabelFrame(root, text=col, font="22")
        df = self.analysis.get_df()
        range_l = tk.Label(desc, text=f"Range: {df[col].min():.2f} - {df[col].max():.2f}",
                           font='16', anchor='w', justify='left')
        mean = tk.Label(desc, text=f"Mean: {df[col].mean():.2f}",
                        font='16', anchor='w', justify='left')
        median = tk.Label(desc, text=f"Median: {df[col].median():.2f}",
                          font='16', anchor='w', justify='left')
        mode_val = df[col].mode()
        count_mode_val = df[df[col] == mode_val[0]].count()[col]
        mode = tk.Label(desc, text=f"Mode: {mode_val[0]}, Count: {count_mode_val}",
                        font='16', anchor='w', justify='left')
        sd = tk.Label(desc, text=f"SD: {df[col].std():.2f}", font='16',
                      anchor='w', justify='left')
        var = tk.Label(desc, text=f"Variance: {df[col].var():.2f}", font='16', anchor='w', justify='left')
        q1 = df[col].quantile(0.25)
        q1_l = tk.Label(desc, text=f"Q1: {q1:.2f}", font='16', anchor='w', justify='left')
        q3 = df[col].quantile(0.75)
        q3_l = tk.Label(desc, text=f"Q1: {q3:.2f}", font='16', anchor='w', justify='left')
        iqr = q3 - q1
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

    def exit(self):
        """ Save and Exit the Application"""
        confirmation = tk.messagebox.askokcancel(title="Exit Application",
                                                 message="Are you sure you want to exit?")
        if confirmation:
            self.analysis.save_all()
            self.quit()
