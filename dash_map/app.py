"""This is the main file for the Dash application.
It initializes the Dash app, sets up the layout, and defines the callback for page navigation.
It imports the necessary components from Dash and the layout module.
The application consists of a main index page with navigation links and an interactive map,
and two additional pages (Page 1 and Page 2) with content and navigation back to the main page.
The app is run in debug mode for development purposes.

Needed libraries:
- dash
- dash_leaflet
- pandas

To launch the app be at OP_MINI_PROJECT directory and use the command:
Linux/macOS:
python3 app.py
Windows:
python app.py
"""

import dash
from dash import html
from dash import dcc  # Додайте імпорт dcc, якщо його ще немає
from dash.dependencies import Input, Output
from assets.layout import index_page, page_1_layout, page_2_layout  # Імпортуємо макети
import pandas as pd

# Завантаження даних з CSV-файлу
filepath = './shelters_coords.csv'
shelters_df = pd.read_csv(filepath)

# Фільтруємо лише ті записи, які мають координати
shelters_df = shelters_df.dropna(subset=['latitude', 'longitude'])
shelters_df = shelters_df.drop(columns=['account_number',
                'ability_to_publish_information', 'district', 'community'])
# print(shelters_df.columns)
# Отримуємо координати укриттів
# shelters_coords = shelters_df[['type_of_room', 'capacity_of_persons', 'latitude', 'longitude', 'street', 'building_number']].values.tolist()

# Передаємо координати в макет
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),  # Відстеження змін URL
    dcc.Store(id='bounds-store'),  # Сховище для меж карти
    html.Div(id='bounds-display', style={'marginTop': '20px'}),  # Відображення меж карти
    html.Div(id='page-content')  # Контейнер для сторінок
])

@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')#, Input('map', 'bounds') # Додаємо bounds-store для отримання меж
)
def display_page(pathname) -> html.Div:
    """
    Display the appropriate page based on the URL pathname.
    :param pathname: The current URL pathname.
    :return: The layout of the corresponding page.
    """
    # print(data)
    if pathname == '/page-1':
        return page_1_layout  # Повертаємо статичний макет
    if pathname == '/page-2':
        return page_2_layout  # Повертаємо статичний макет
    # if bounds:
    #     south, west, north, east = bounds[0][0], bounds[0][1], bounds[1][0], bounds[1][1]
    #     print(f"Bounds updated: South={south}, West={west}, North={north}, East={east}")
    return index_page(shelters_df, {'south': 49.8, 'west': 23.9, 'north': 49.9, 'east': 24.1})  # Передаємо shelters_df тільки для index_page

@app.callback(
    Output('bounds-store', 'data'),  # Update dcc.Store's data property
    Input('map', 'bounds')  # Listen for map bounds changes
)
def update_bounds(bounds):
    if bounds:
        south, west, north, east = bounds[0][0], bounds[0][1], bounds[1][0], bounds[1][1]
        print(f"Bounds updated: South={south}, West={west}, North={north}, East={east}")
        return {'south': south, 'west': west, 'north': north, 'east': east}
    return {}

# @app.callback(
#     Output('bounds-display', 'children'),  # Update display with bounds data
#     Input('bounds-store', 'data')  # Use data from dcc.Store
# )
# def display_bounds(bounds_data):
#     if bounds_data:
#         return f"Bounds: South={bounds_data['south']}, West={bounds_data['west']}, North={bounds_data['north']}, East={bounds_data['east']}"
#     return "No bounds available"

if __name__ == "__main__":
    app.run(debug=True)
