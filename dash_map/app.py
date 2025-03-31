"""This is the main file for the Dash application.
It initializes the Dash app, sets up the layout, and defines the callback for page navigation.
It imports the necessary components from Dash and the layout module.
The application consists of a main index page with navigation links and an interactive map,
and two additional pages (Page 1 and Page 2) with content and navigation back to the main page.
The app is run in debug mode for development purposes.
"""

import dash
from dash import html
from dash.dependencies import Input, Output
from assets.layout import index_page, page_1_layout, page_2_layout  # Імпортуємо макети
import pandas as pd

# Завантаження даних з CSV-файлу
filepath = '/mnt/667E8B397E8B00D3/UCU/Fundamentals_of_programming/op_mini_project/shelters_coords.csv'
shelters_df = pd.read_csv(filepath)

# Фільтруємо лише ті записи, які мають координати
shelters_df = shelters_df.dropna(subset=['latitude', 'longitude'])

# Отримуємо координати укриттів
shelters_coords = shelters_df[['latitude', 'longitude']].values.tolist()

# Передаємо координати в макет
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.layout = index_page(shelters_coords)  # Передаємо shelters_coords у макет

@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)

def display_page(pathname) -> html.Div:
    """
    Display the appropriate page based on the URL pathname."
    :param pathname: The current URL pathname.
    :return: The layout of the corresponding page.
    """
    if pathname == '/page-1':
        return page_1_layout
    if pathname == '/page-2':
        return page_2_layout
    return index_page # Default to index page

if __name__ == "__main__":
    app.run(debug=True)
