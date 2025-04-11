"""
This module defines the layout for a Dash web application.

It includes:
- The main index page with navigation links and an interactive map.
- Layouts for additional pages (Page 1 and Page 2) with simple content
and navigation back to the main page.

The module uses Dash components (`html`, `dcc`) and Dash Leaflet (`dl`) for building the UI.
"""

from dash import dcc, html
import dash_leaflet as dl
import pandas as pd

def select_top_200(shelters_df: pd.DataFrame, bounds: dict[str, float]) -> pd.DataFrame:
    """
    Select the top 200 shelters based on their capacity within the visible map bounds.
    :param shelters_df: DataFrame containing shelter data.
    :param north: Northern latitude of the visible map area.
    :param south: Southern latitude of the visible map area.
    :param east: Eastern longitude of the visible map area.
    :param west: Western longitude of the visible map area.
    :return: DataFrame with the top 200 shelters within the bounds.
    """
    # Фільтруємо укриття, які знаходяться в межах видимої області карти
    # bounds[0][0], bounds[0][1], bounds[1][0], bounds[1][1]
    if bounds is None:
        bounds = {'south': 49.8, 'west': 23.9, 'north': 49.9, 'east': 24.1}
        bounds = [[49.8, 23.9], [49.9, 24.1]]
    shelters_df = shelters_df[
        (shelters_df['latitude'] <= bounds['north']) &
        (shelters_df['latitude'] >= bounds['south']) &
        (shelters_df['longitude'] <= bounds['east']) &
        (shelters_df['longitude'] >= bounds['west'])
    ]
    # Сортуємо за місткістю та вибираємо топ-500
    return shelters_df.nlargest(500, 'capacity_of_persons')
    # sorted_shelters = shelters_df.sort_values(by='capacity_of_persons', ascending=False)
    # return sorted_shelters.head(800)


index_page = html.Div([
        html.H1("Мапа укриттів", className='page-title'),
        html.Div([
            dcc.Link('Перейти на сторінку 1', href='/page-1', className='button-link'),
            html.Br(),
            dcc.Link('Перейти на сторінку 2', href='/page-2', className='button-link')
        ], className='button-container'),

        dl.Map(
            id="map",  # Added id to track map bounds
            center=[49.841427, 24.020676],
            zoom=12,
            children=[
                dl.TileLayer(),
                dl.LayerGroup(id="shelter-layer"),  # Додаємо маркери укриттів на карту
            ],
            bounds=[[49.8, 23.9], [49.9, 24.1]],
            className='map-container'
        ),
        dcc.Store(id='bounds-store'),  # Added dcc.Store for storing bounds
    ])


# page_1_layout = html.Div([
#     html.H1("Сторінка 1"),
#     html.P("Це сторінка номер 1."),
#     dcc.Link('Назад на головну', href='/')
# ])

page_1_layout =  html.Div([
    html.Div(className="login-container", children=[
        html.H2("Login", className="login-title"),
        dcc.Input(id="username", type="text", placeholder="Username", className="input-box"),
        dcc.Input(id="password", type="password", placeholder="Password", className="input-box"),
        html.Button("Login", id="login-button", n_clicks=0, className="login-button"),
        html.Div(id="login-output", className="error-message"),
        html.A("Back to Map", href="/map", className="back-link")
    ])
], className="main-container")


page_2_layout = html.Div([
    html.H1("Сторінка 2"),
    html.P("Це сторінка номер 2."),
    dcc.Link('Назад на головну', href='/')
])
