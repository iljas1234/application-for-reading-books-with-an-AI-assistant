#импорт модулей
import pandas as pd
import tkinter as tk
import tkinter.ttk as ttk
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
from pathlib import Path
import numpy as np
#виджет для запросов к ии
class AI_recommendation_Window(tk.Frame):
    def __init__(self, master=None, k=None, metric='cosine', show_distance=False):
        tk.Frame.__init__(self, master)
        self.k = k
        self.metric = metric
        self.show_distance = show_distance
        self.pack()
        self.set_data()
        self.create_widgets()
        self.AI()


    #загруска данных
    def set_data(self):
        self.data = pd.read_csv("books_df_clean.csv", encoding="utf-8", on_bad_lines="skip")
        self.books_user_ratings_path = Path('books_user_ratings_df.csv')
        self.books_user_ratings_df = pd.read_csv(self.books_user_ratings_path, on_bad_lines="skip")
        #self.books_user_ratings_df = self.books_user_ratings_df.reset_index(level=['User_id'])
        self.X, self.user_mapper, self.book_mapper = create_matrix(self.books_user_ratings_df)
        self.colname_list = ['Title', 'description', 'authors', 'categories']
        self.width_list = [200, 300, 150, 200]
        self.search_col = "Id"

    #запуск всех функций и создание PanedWindow
    def create_widgets(self):
        self.pw_main = ttk.PanedWindow(self, orient="vertical")
        self.pw_main.pack(expand=True, fill=tk.BOTH, side="left")
        self.pw_top = ttk.PanedWindow(self.pw_main, orient="horizontal", height=25)
        self.pw_main.add(self.pw_top)
        self.pw_bottom = ttk.PanedWindow(self.pw_main, orient="vertical")
        self.pw_main.add(self.pw_bottom)
        self.creat_input_frame(self.pw_top)
        self.create_tree(self.pw_bottom)

    #создание фрейма для ввода запроса
    def creat_input_frame(self, parent):
        fm_input = ttk.Frame(parent, )
        parent.add(fm_input)
        lbl_keyword = ttk.Label(fm_input, text="запрос для ИИ", width=10)
        lbl_keyword.grid(row=1, column=1, padx=2, pady=2)
        self.keyword = tk.StringVar()
        ent_keyword = ttk.Entry(fm_input, justify="left", textvariable=self.keyword)
        ent_keyword.grid(row=1, column=2, padx=2, pady=2)
        ent_keyword.bind("<Return>", self.AI_find_book)

    #создание Treeview для вывода результата поиска с информацией о книге
    def create_tree(self, parent):
        self.result_text = tk.StringVar()
        lbl_result = ttk.Label(parent, textvariable=self.result_text)
        parent.add(lbl_result)
        self.tree = ttk.Treeview(parent)
        self.tree["column"] = self.colname_list
        self.tree["show"] = "headings"
        self.tree.bind("<Double-1>", self.onDuble)
        for i, (colname, width) in enumerate(zip(self.colname_list, self.width_list)):
            self.tree.heading(i, text=colname)
            print(colname)
            self.tree.column(i, width=width)
        parent.add(self.tree)

    def AI(self):
        # self.book_id = self.book_id["User_id"][0]
        self.k += 1
        self.kNN = NearestNeighbors(n_neighbors=self.k, algorithm='brute', metric=self.metric)
        self.kNN.fit(self.X)

    def AI_find_book(self, event=None):
        self.book_id = self.keyword.get()
        self.book_id = self.books_user_ratings_df[self.books_user_ratings_df["Title"].str.contains(self.book_id, na=False)]
        self.book_ind = self.book_mapper[self.book_id['Book-ID'].iloc[0]]
        book_vec = self.X[self.book_ind]
        book_vec = book_vec.reshape(1, -1)
        neighbour = self.kNN.kneighbors(book_vec, return_distance=self.show_distance)
        n = self.data[self.data[self.search_col] == neighbour.item(1)]
        for i in range(2, self.k):
            h = self.data[self.data[self.search_col] == neighbour.item(i)]
            n = pd.concat([n, h])
        self.update_tree_by_search_result(n)
    #вывод книг
    def update_tree_by_search_result(self, result):
        self.tree.delete(*self.tree.get_children())
        self.result_text.set(f"search results:{len(result)}")
        for _, row in result.iterrows():
            print(row)
            self.tree.insert("", "end", values=row[self.colname_list].to_list())

    #нажатия на книгу
    def onDuble(self, event):
        for item in self.tree.selection():
            print(self.tree.item(item)["values"])
#виджет для поисковика
class SearchWindow(tk.Frame):
    def __init__(self, master=None, parent=None):
        tk.Frame.__init__(self, master)
        self.pack()
        self.set_data()
        self.create_widgets()

    #загруска данных
    def set_data(self):
        self.data = pd.read_csv("books_df_clean.csv", encoding="utf-8", on_bad_lines="skip")
        self.colname_list = ['Title', 'description', 'authors', 'categories']
        self.width_list = [200, 300, 150, 200]
        self.search_col = "Title"

    #запуск всех функций и создание PanedWindow
    def create_widgets(self):
        self.pw_main = ttk.PanedWindow(self, orient="vertical")
        self.pw_main.pack(expand=True, fill=tk.BOTH, side="left")
        self.pw_top = ttk.PanedWindow(self.pw_main, orient="horizontal", height=25)
        self.pw_main.add(self.pw_top)
        self.pw_bottom = ttk.PanedWindow(self.pw_main, orient="vertical")
        self.pw_main.add(self.pw_bottom)
        self.create_input_frame(self.pw_top)
        self.create_tree(self.pw_bottom)

    #создание фрейма для ввода запроса
    def create_input_frame(self, parent):
        fm_input = ttk.Frame(parent, )
        parent.add(fm_input)
        lbl_keyword = ttk.Label(fm_input, text="что ищите", width=10)
        lbl_keyword.grid(row=1, column=1, padx=2, pady=2)
        self.keyword = tk.StringVar()
        ent_keyword = ttk.Entry(fm_input, justify="left", textvariable=self.keyword)
        ent_keyword.grid(row=1, column=2, padx=2, pady=2)
        ent_keyword.bind("<Return>", self.search)

    #создание Treeview для вывода результата поиска с информацией о книге
    def create_tree(self, parent):
        self.result_text = tk.StringVar()
        lbl_result = ttk.Label(parent, textvariable=self.result_text)
        parent.add(lbl_result)
        self.tree = ttk.Treeview(parent)
        self.tree["column"] = self.colname_list
        self.tree["show"] = "headings"
        self.tree.bind("<Double-1>", self.onDuble)
        for i, (colname, width) in enumerate(zip(self.colname_list, self.width_list)):
            self.tree.heading(i, text=colname)
            print(colname)
            self.tree.column(i, width=width)
        parent.add(self.tree)

    #обновление поисковых данных после нажатия enter 1
    def search(self, event=None):
        keyword = self.keyword.get()
        print(keyword)
        result = self.data[self.data[self.search_col].str.contains(keyword, na=False)]
        print(result)
        self.update_tree_by_search_result(result)

    #вывод книг
    def update_tree_by_search_result(self, result):
        self.tree.delete(*self.tree.get_children())
        self.result_text.set(f"search results:{len(result)}")
        for _, row in result.iterrows():
            print(row)
            self.tree.insert("", "end", values=row[self.colname_list].to_list())

    #нажатия на книгу
    def onDuble(self, event):
        for item in self.tree.selection():
            print(self.tree.item(item)["values"])

# создание матрицы
def create_matrix(df):
    #нахождение уникальных элементов
    N = len(df['User_id'].unique())
    M = len(df['Book-ID'].unique())

    # сравнивание уникальных ID с индексом
    user_mapper = dict(zip(np.unique(df['User_id']), list(range(N))))
    book_mapper = dict(zip(np.unique(df['Book-ID']), list(range(M))))

    """# сопостовление индекса с ID
    user_inv_mapper = dict(zip(list(range(N)), np.unique(df['User_id'])))
    book_inv_mapper = dict(zip(list(range(M)), np.unique(df['Book-ID'])))"""

    #список индексов
    user_index = [user_mapper[i] for i in df['User_id']]
    book_index = [book_mapper[i] for i in df['Book-ID']]

    #создание матрицы
    X = csr_matrix((df['Book-ID'], (book_index, user_index)), shape=(M, N))
    #вывод
    return X, user_mapper, book_mapper


def main():

    root = tk.Tk()

    # создаем набор вкладок
    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill=tk.BOTH)

    # создаем фреймвов
    frame1 = ttk.Frame(notebook)
    SearchWindow(master=frame1)
    frame1.pack(fill=tk.BOTH, expand=True)

    frame2 = ttk.Frame(notebook)
    AI_recommendation_Window(master=frame2,  k=10)
    frame2.pack(fill=tk.BOTH, expand=True)

    # добавляем фреймы в качестве вкладок
    notebook.add(frame1, text="поисковик")
    notebook.add(frame2, text="AI рекомендации")

    root.mainloop()

if __name__ == "__main__":
    main()
