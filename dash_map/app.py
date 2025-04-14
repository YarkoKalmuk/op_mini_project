import math
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_leaflet as dl
import pandas as pd
import dash_bootstrap_components as dbc

from assets.layout import index_page, page_1_layout, page_2_layout, page_3_layout, select_top_200
from find_shelter_algo import compute_route  # Імпортуємо функцію для маршруту

import sqlite3

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


conn = sqlite3.connect('./instance/shelters.sqlite')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS reviews (
    shelter_id VARCHAR(128) NOT NULL,
    review_text VARCHAR(256) NOT NULL
)
''')
conn.close()


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
    if pathname == '/review':
        return page_3_layout  # Сторінка з відгуками
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
                                       f"місткість: {row['capacity_of_persons']}"),
                            # Додаємо лінк для переходу на сторінку відгуків
                            dl.Popup([
                                html.A(f"Перейти до відгуків", href=f"/review?shelter_id={row['street']}_{row['building_number']}")
                            ])
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
    Output("route-message", "children"),
    Input("find-route-btn-main", "n_clicks"),
    State("address-input", "value"),
    prevent_initial_call=True
)
def handle_route_on_main(n_clicks, address):
    if not address:
        return [], "❗ Будь ласка, введіть адресу."
    try:
        name, minutes, coords = compute_route(address, 'shelters_coords.csv')
        if name is None and coords is None:
            return [], "❗ Початкова адреса не була знайдена. Спробуйте ще раз."
        if not coords or len(coords) < 2:
            return [], "⚠️ Укриття занадто близько. Побудовано пряму лінію."
        start = coords[0]
        end = coords[-1]
        return [
            [
                dl.Polyline(positions=coords, color='red', weight=5),
                dl.Marker(position=start, children=dl.Tooltip("Ви тут 🧍")),
                dl.Marker(position=end, children=dl.Tooltip(f"Укриття: {name} (≈ {minutes} хв) 🛡️"))
            ],
            ""
        ]
    except Exception as e:
        print(f"Помилка: {e}")
        return [], "🚫 Сталася помилка при побудові маршруту. Перевірте адресу або спробуйте ще раз."


@app.callback(
    Output('reviews-container', 'children'),
    Input('url', 'pathname'),
    State('url', 'search')
)
def display_reviews(pathname, search):
    if pathname == '/review':
        # Тут можна отримати id укриття з query параметра
        shelter_id = search.split('=')[1] if search else ''
        # Завантажити відгуки з бази даних або з іншого джерела
        reviews = get_reviews(shelter_id)
        return html.Div([html.P(review) for review in reviews])
    return []

def get_reviews(shelter_id):
    conn = sqlite3.connect('./instance/shelters.sqlite')
    cursor = conn.cursor()
    all_reviews = cursor.execute('SELECT * FROM reviews WHERE shelter_id = ?', (shelter_id,)).fetchall()
    reviews = []
    for review in all_reviews:
        reviews.append(review[1])
    conn.close()
    return reviews

@app.callback(
    Output('new-review', 'value'),
    Input('submit-review', 'n_clicks'),
    State('new-review', 'value'),
    State('url', 'search'),
    prevent_initial_call=True
)
def submit_review(n_clicks, review_text, search):
    if n_clicks > 0 and review_text:
        shelter_id = search.split('=')[1] if search else ''
        # Тут додати відгук в базу даних
        save_review(review_text, shelter_id)
        return ''  # Очищаємо поле вводу після додавання відгуку
    return review_text

def save_review(review_text, shelter_id):
    conn = sqlite3.connect('./instance/shelters.sqlite')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO reviews VALUES (?, ?)', (shelter_id, review_text,))
    conn.commit()
    print(f"Saving review: {review_text}")
    # Ти можеш зберігати відгуки в базі даних, тут приклад з виведенням в консоль.
    conn.close()



if __name__ == "__main__":
    app.run(debug=True)
