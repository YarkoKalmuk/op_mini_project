"""
This is the main file for the Dash application.
It initializes the Dash app, sets up the layout, and defines the callback for page navigation.
It imports the necessary components from Dash and the layout module.
The application consists of a main index page with navigation links and an interactive map,
and two additional pages (Page 1 and Page 2) with content and navigation back to the main page.
The app is run in debug mode for development purposes.

Needed libraries:
- dash
- dash_leaflet
- pandas
- dash_bootstrap_components

To launch the app be at OP_MINI_PROJECT directory and use the command:
Linux/macOS:
python3 app.py
Windows:
python app.py
"""

import math
import dash
from dash import html, dcc  # Додайте імпорт dcc, якщо його ще немає
from dash.dependencies import Input, Output, State
import dash_leaflet as dl
from assets.layout import index_page, page_1_layout, page_2_layout, select_top_200  # Імпортуємо макети
import pandas as pd
import dash_bootstrap_components as dbc

# Завантаження даних з CSV-файлу
filepath = './../shelters_coords.csv'
shelters_df = pd.read_csv(filepath)

# Фільтруємо лише ті записи, які мають координати
shelters_df = shelters_df.dropna(subset=['latitude', 'longitude'])
shelters_df = shelters_df.drop(columns=['account_number',
                'ability_to_publish_information', 'district', 'community'])
shelters_df.loc[shelters_df['type_of_room'] =='Сховище', 'colour'] = 'red'
shelters_df.loc[shelters_df['type_of_room'] !='Сховище', 'colour'] = 'blue'

# Передаємо координати в макет
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),  # Відстеження змін URL
    dcc.Store(id='bounds-store'),  # Сховище для меж карти
    html.Div(id='bounds-display'),  # Відображення меж карти
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
    return index_page


@app.callback(
    Output('bounds-store', 'data'),  # Update dcc.Store's data property
    Input('map', 'bounds')  # Listen for map bounds changes
)
def update_bounds(bounds):
    """
    Update the bounds in dcc.Store when the map bounds change.
    :param bounds: The current bounds of the map.
    :return: A dictionary with the bounds data.
    """
    if bounds:
        return {
            'south': bounds[0][0], 'west': bounds[0][1],
            'north': bounds[1][0], 'east': bounds[1][1]
            }
    return {}



@app.callback(
    Output("shelter-layer", "children"),  # Update the shelter layer on the map
    Input("bounds-store", "data")
)
def update_shelter_markers(bounds):
    """
    Update the shelter markers on the map based on the current bounds.
    :param bounds: The current bounds of the map.
    :return: A list of CircleMarker components for the shelters within the bounds.
    """
    global shelters_df
    shelter_markers = select_top_200(shelters_df, bounds)
    return [
        dl.CircleMarker(center=[row['latitude'], row['longitude']],
                        radius=3*math.log(row['capacity_of_persons']/20),
                        color=row['colour'],
                        fillOpacity=0.6,
                        children=[
                            dl.Tooltip(f"{row['type_of_room']}, "
                                       f"{row['street']} {row['building_number']}, "
                                       f"місткість: {row['capacity_of_persons']}, ")
                        ])
        for _, row in shelter_markers.iterrows()
    ]

# @app.callback(
#     Output("debug-output", "children"),
#     Input("bounds-store", "data")
# )
# def show_bounds(bounds):
#     return f"Bounds: {bounds}" if bounds else "Немає даних"


# Callback to handle login
@app.callback(
    Output("login-output", "children"),
    Input("login-button", "n_clicks"),
    State("username", "value"),
    State("password", "value"),
    prevent_initial_call=True
)
def validate_login(n_clicks, username, password):
    if username == "admin" and password == "password":
        return "Login successful! Redirecting..."
    return "Invalid credentials. Try again."

import sys
import os
from geopy.geocoders import Nominatim
import osmnx as ox
import networkx as nx
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from find_shelter import dj  # функція Дейкстри

# Підготовка графа
GRAPH_FILE = "./../lviv_graph.graphml"
if os.path.exists(GRAPH_FILE):
    G = ox.load_graphml(GRAPH_FILE)
else:
    G = ox.graph_from_place("Lviv, Ukraine", network_type="walk", simplify=True)
    ox.save_graphml(G, GRAPH_FILE)

graph_dict = {node: {} for node in G.nodes()}
for u, v, data in G.edges(data=True):
    length = data.get("length", 1)
    graph_dict[u][v] = length

@app.callback(
    Output("route-layer", "children"),
    Input("submit-address", "n_clicks"),
    State("address-input", "value"),
    prevent_initial_call=True
)
def find_and_draw_route(n_clicks, address):
    if not address:
        return []

    # Геокодування адреси
    geolocator = Nominatim(user_agent="shelter_finder")
    location = geolocator.geocode(address + ", Львів, Україна")
    if not location:
        return []

    user_point = (location.latitude, location.longitude)
    user_node = ox.distance.nearest_nodes(G, user_point[1], user_point[0])

    # Збір укриттів
    shelter_nodes = {}
    for _, row in shelters_df.iterrows():
        try:
            lat, lon = row["latitude"], row["longitude"]
            shelter_node = ox.distance.nearest_nodes(G, lon, lat)
            shelter_nodes[f"{row['street']} {row['building_number']}"] = shelter_node
        except:
            continue

    # Знаходимо найкоротший шлях
    distances, previous_nodes = dj(graph_dict, user_node)
    closest_shelter_name, shelter_node = min(
        shelter_nodes.items(),
        key=lambda item: distances.get(item[1], float('inf'))
    )

    # Відновлюємо маршрут
    path = []
    node = shelter_node
    while node is not None:
        path.append(node)
        node = previous_nodes.get(node)
    path = path[::-1]

    route_coords = [(G.nodes[n]["y"], G.nodes[n]["x"]) for n in path]

    return [
        dl.Polyline(positions=route_coords, color="red", weight=5),
        dl.Marker(position=route_coords[0], children=dl.Tooltip("Ви")),
        dl.Marker(position=route_coords[-1], children=dl.Tooltip("Укриття")),
    ]


if __name__ == "__main__":
    app.run(debug=True)
