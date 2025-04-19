import math
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_leaflet as dl
import pandas as pd
import dash_bootstrap_components as dbc

from assets.layout import index_page, page_3_layout, select_top_200
from find_shelter_algo import compute_route  # Імпортуємо функцію для маршруту
from assets.layout import register_layout, login_layout
import sqlite3
from hashlib import sha256

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
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    token TEXT NOT NULL
)
''')
cursor.execute('''CREATE TABLE IF NOT EXISTS reviews (
    shelter_id VARCHAR(128) NOT NULL,
    review_text VARCHAR(256) NOT NULL,
    username TEXT NOT NULL
)
''')
conn.close()


# 📄 Роутинг між сторінками
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/login':
        return login_layout
    if pathname == '/register':
        return register_layout
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

@app.callback(
    Output("login-output", "children"),
    Output("user-token", "data"),
    Input("login-button", "n_clicks"),
    State("login-email", "value"),
    State("login-password", "value"),
    prevent_initial_call=True
)
def handle_login(n_clicks, email, password):
    conn = sqlite3.connect('./instance/shelters.sqlite')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    input_ = f'{email}{password}dev'
    token = sha256(input_.encode('utf-8')).hexdigest()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    if user is not None and user['token'] == token:
        return 'Логін успішний', token
    return 'Або електронна пошта не правильна або пароль', dash.no_update

@app.callback(
    Output("register-output", "children"),
    Input("register-button", "n_clicks"),
    State("reg-username", "value"),
    State("reg-email", "value"),
    State("reg-password", "value"),
    prevent_initial_call=True
)
def handle_register(n_clicks, username, email, password):
    conn = sqlite3.connect('./instance/shelters.sqlite')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    input_ = f'{email}{password}dev'
    token = sha256(input_.encode('utf-8')).hexdigest()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    users_with_similar_email = cursor.fetchall()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    users_with_similar_username = cursor.fetchall()
    if len(users_with_similar_email) > 0:
        return 'Користувач із таким email уже зареєстрований'
    if len(users_with_similar_username) > 0:
        return 'Користувач із таким username уже зареєстрований'
    cursor.execute('INSERT INTO users (username, email, token) VALUES (?, ?, ?)', (username, email, token))
    conn.commit()
    conn.close()
    return 'Користувача зареєстровано, перейдіть на сторінку логіну і авторизуйтесь'


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
    reviews = [f"{review[2]}: {review[1]}" for review in all_reviews]
    conn.close()
    return reviews

@app.callback(
    Output('new-review', 'value'),
    Input('submit-review', 'n_clicks'),
    State('new-review', 'value'),
    State('url', 'search'),
    State('user-token', 'data'),
    prevent_initial_call=True
)
def submit_review(n_clicks, review_text, search, token):
    if n_clicks > 0 and review_text and token:
        shelter_id = search.split('=')[1] if search else ''
        conn = sqlite3.connect('./instance/shelters.sqlite')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT username FROM users WHERE token = ?', (token,))
        user = cursor.fetchone()
        conn.close()
        if user:
            username = user['username']
            save_review(review_text, shelter_id, username)
        return ''  # очищення поля
    return review_text

def save_review(review_text, shelter_id, username):
    conn = sqlite3.connect('./instance/shelters.sqlite')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO reviews VALUES (?, ?, ?)', (shelter_id, review_text, username,))
    conn.commit()
    print(f"Saving review: {review_text} від {username}")
    # Ти можеш зберігати відгуки в базі даних, тут приклад з виведенням в консоль.
    conn.close()



if __name__ == "__main__":
    app.run(debug=True)
