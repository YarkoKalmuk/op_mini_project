"""
This module defines the layout for a Dash web application.

It includes:
- The main index page with navigation links and an interactive map.
- Layouts for additional pages (Page 1 and Page 2) with simple content and navigation back to the main page.

The module uses Dash components (`html`, `dcc`) and Dash Leaflet (`dl`) for building the UI.
"""

from dash import dcc, html
import dash_leaflet as dl

index_page = html.Div([
    html.H1("Головна сторінка", className='page-title'),
    html.Div([
        dcc.Link('Перейти на сторінку 1', href='/page-1', className='button-link'),
        html.Br(),
        dcc.Link('Перейти на сторінку 2', href='/page-2', className='button-link')
    ], className='button-container'),

    dl.Map(center=[50.45, 30.52], zoom=6, children=[
        dl.TileLayer(),
        dl.Marker(position=[50.45, 30.52], children=[
            dl.Tooltip("Київ, Україна"),
            dl.Popup("Це столиця України!")
        ]),
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
