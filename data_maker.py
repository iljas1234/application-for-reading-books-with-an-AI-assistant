#импорт модулей
import pandas as pd
from pathlib import Path
import numpy as np

#загруска датасетов
books_path = Path('books_data.csv')
ratings_path = Path('Books_rating.csv')
books_df = pd.read_csv(books_path, on_bad_lines="skip")
users_ratings_df = pd.read_csv(ratings_path, on_bad_lines="skip")

#очистка от лишнего муссора
books_df['authors'] = books_df['authors'].str.lower().str.replace("['", '')
books_df['authors'] = books_df['authors'].str.lower().str.replace("']", '')
books_df['categories'] = books_df['categories'].str.lower().str.replace("['", '')
books_df['categories'] = books_df['categories'].str.lower().str.replace("']", '')

#именование индекстов для удобной работы
books_df.reset_index(inplace=True)
books_df.rename(columns = {'index':'Id', 0:'Book-ID'}, inplace=True)

#сохранение чистого датасета
books_df.to_csv('books_df_clean.csv', index=False)

#удаление ненужных столбцов для AI
books_df.drop(books_df[["image", 'previewLink', 'infoLink', 'ratingsCount']], inplace=True, axis=1)
users_ratings_df = users_ratings_df.dropna()[['Id', "User_id", 'Title', "review/score", "review/time", "review/summary"]]
books_user_ratings_df = pd.merge(users_ratings_df, books_df, on='Title')

# Создайте массив уникальных значений ISBN, преобразуйте в series, затем в DataFrame
#нахождение уникальных элементов ID
book_ids = pd.unique(books_user_ratings_df['Id'].ravel())
#преобразование в обномерный массив для очистки от мусора
book_ids = pd.Series(np.arange(len(book_ids)), book_ids)
#возврат в формат таблицы
book_ids = pd.DataFrame(book_ids)
#именование индекстов для удобной работы
book_ids.reset_index(inplace=True)
book_ids.rename(columns={'index':'Id', 0:'Book-ID'}, inplace=True)

#обьеденение таблиц
books_user_ratings_df = pd.merge(books_user_ratings_df, book_ids, on='Id')

#сохранение конечного результата
books_user_ratings_df.to_csv('books_user_ratings_df.csv', index=False)




