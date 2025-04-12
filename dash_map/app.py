import math
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_leaflet as dl
import pandas as pd
import dash_bootstrap_components as dbc

from assets.layout import index_page, page_1_layout, page_2_layout, select_top_200
from find_shelter_algo import compute_route  # Імпортуємо функцію для маршруту

# Завантаження укриттів
filepath = './shelters_coords.csv'
shelters_df = pd.read_csv(filepath)
shelters_df = shelters_df.dropna(subset=['latitude', 'longitude'])
shelters_df = shelters_df.drop(columns=['account_number', 'ability_to_publish_information', 'district', 'community'])
shelters_df.loc[shelters_df['type_of_room'] == 'Сховище', 'colour'] = 'red'
shelters_df.loc[shelters_df['type_of_room'] != 'Сховище', 'colour'] = 'blue'

# Ініціалізація додатку
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='bounds-store'),
    html.Div(id='page-content')
])

# 📄 Роутинг між сторінками
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/page-1':
        return page_1_layout
    if pathname == '/page-2':
        return page_2_layout
    return index_page

# 🗺️ Оновлення меж карти
@app.callback(
    Output('bounds-store', 'data'),
    Input('map', 'bounds')
)
def update_bounds(bounds):
    if bounds:
        return {
            'south': bounds[0][0], 'west': bounds[0][1],
            'north': bounds[1][0], 'east': bounds[1][1]
        }
    return {}

# 🧭 Маркери укриттів
@app.callback(
    Output("shelter-layer", "children"),
    Input("bounds-store", "data")
)
def update_shelter_markers(bounds):
    global shelters_df
    shelter_markers = select_top_200(shelters_df, bounds)
    return [
        dl.CircleMarker(center=[row['latitude'], row['longitude']],
                        radius=3 * math.log(row['capacity_of_persons'] / 20),
                        color=row['colour'],
                        fillOpacity=0.6,
                        children=[
                            dl.Tooltip(f"{row['type_of_room']}, "
                                       f"{row['street']} {row['building_number']}, "
                                       f"місткість: {row['capacity_of_persons']}")
                        ])
        for _, row in shelter_markers.iterrows()
    ]

# 🔐 Логін
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

@app.callback(
    Output("route", "children"),
    Input("find-route-btn-main", "n_clicks"),
    State("address-input", "value"),
    prevent_initial_call=True
)
def handle_route_on_main(n_clicks, address):
    if not address:
        return []

    try:
        name, minutes, coords = compute_route(address, 'shelters_coords.csv')
        if not coords or len(coords) < 2:
            return []

        start = coords[0]
        end = coords[-1]

        return [
            dl.Polyline(positions=coords, color='red', weight=5),
            dl.Marker(position=start, children=dl.Tooltip("Ви тут 🧍")),
            dl.Marker(position=end, children=dl.Tooltip(f"Укриття: {name} (≈ {minutes} хв) 🛡️"))
        ]
    except Exception as e:
        print(f"Помилка: {e}")
        return []




if __name__ == "__main__":
    app.run(debug=True)
