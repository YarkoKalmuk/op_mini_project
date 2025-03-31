"""
This module defines the layout for a Dash web application.

It includes:
- The main index page with navigation links and an interactive map.
- Layouts for additional pages (Page 1 and Page 2) with simple content and navigation back to the main page.

The module uses Dash components (`html`, `dcc`) and Dash Leaflet (`dl`) for building the UI.
"""

from dash import dcc, html
import dash_leaflet as dl

def index_page(shelters_coords):
    # Створюємо маркери для укриттів
    shelter_markers = [
        dl.CircleMarker(center=[lat, lon], radius=5, color='blue', fillColor='blue', fillOpacity=0.6)
        for lat, lon in shelters_coords
    ]

    return html.Div([
        html.H1("Мапа укриттів", className='page-title'),
        html.Div([
            dcc.Link('Перейти на сторінку 1', href='/page-1', className='button-link'),
            html.Br(),
            dcc.Link('Перейти на сторінку 2', href='/page-2', className='button-link')
        ], className='button-container'),

        dl.Map(center=[49.841427, 24.020676], zoom=12, children=[
            dl.TileLayer(),
            *shelter_markers  # Додаємо маркери укриттів на карту
        ], className='map-container')
    ])

page_1_layout = html.Div([
    html.H1("Сторінка 1"),
    html.P("Це сторінка номер 1."),
    dcc.Link('Назад на головну', href='/')
])

page_2_layout = html.Div([
    html.H1("Сторінка 2"),
    html.P("Це сторінка номер 2."),
    dcc.Link('Назад на головну', href='/')
])
