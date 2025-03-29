"""This is the main file for the Dash application.
It initializes the Dash app, sets up the layout, and defines the callback for page navigation.
It imports the necessary components from Dash and the layout module.
The application consists of a main index page with navigation links and an interactive map,
and two additional pages (Page 1 and Page 2) with simple content and navigation back to the main page.
The app is run in debug mode for development purposes.
"""

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from assets.layout import index_page, page_1_layout, page_2_layout  # Імпортуємо макети

app = dash.Dash(__name__, suppress_callback_exceptions=True)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

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
