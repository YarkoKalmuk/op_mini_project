from dash import dcc, html
import dash_leaflet as dl
import pandas as pd

def select_top_200(shelters_df: pd.DataFrame, bounds: dict[str, float]) -> pd.DataFrame:
    if bounds is None:
        bounds = {'south': 49.8, 'west': 23.9, 'north': 49.9, 'east': 24.1}
        bounds = [[49.8, 23.9], [49.9, 24.1]]
    shelters_df = shelters_df[
        (shelters_df['latitude'] <= bounds['north']) &
        (shelters_df['latitude'] >= bounds['south']) &
        (shelters_df['longitude'] <= bounds['east']) &
        (shelters_df['longitude'] >= bounds['west'])
    ]
    return shelters_df.nlargest(500, 'capacity_of_persons')


# Головна сторінка

index_page = html.Div([
    html.H1("Мапа укриттів", className='page-title'),

    dcc.Store(id='user-token', storage_type='local'),

    html.Div([
        html.Div([
            dcc.Input(
                id='address-input',
                type='text',
                placeholder='Введіть повну адресу (наприклад: Вулиця Зелена 20А)',
                className='input-box',
                debounce=True
            ),
            html.Button('Знайти укриття', id='find-route-btn-main', n_clicks=0, className='search-button'),
        ], style={'display': 'flex', 'gap': '10px'}),  # Новий підконтейнер тільки для поля і кнопки

        html.Div(id='route-message', className='status-message')  # Помилка окремо, піде вниз
    ], className='search-container'),

    html.Div(id='auth-section', className='button-container'),

    dl.Map(
        id="map",
        center=[49.841427, 24.020676],
        zoom=12,
        children=[
            dl.TileLayer(),
            dl.LayerGroup(id="shelter-layer"),
            dl.LayerGroup(id="route")
        ],
        bounds=[[49.8, 23.9], [49.9, 24.1]],
        className='map-container'
    ),

    dcc.Store(id='bounds-store'),
])


# Сторінка логіну
login_layout = html.Div([
    html.Div(className="login-container", children=[
        html.H2("Логін", className="login-title"),
        dcc.Input(id="login-email", type="email", placeholder="Email", className="input-box"),
        dcc.Input(id="login-password", type="password", placeholder="Пароль", className="input-box"),
        html.Button("Увійти", id="login-button", n_clicks=0, className="login-button"),
        html.Div(id="login-output"),  # Просто контейнер без класу
        html.A("Назад до мапи", href="/", className="back-link"),
        html.A("Ще не зареєстровані? Натисніть сюди", href="/register", className="back-link"),
        dcc.Store(id='user-token', storage_type='local')
    ])
], className="main-container")

# Додамо нову сторінку для відгуків
review_layout = html.Div([
    dcc.Store(id='user-token', storage_type='local'),
    html.H1("Відгуки про укриття"),
    html.Div(id='reviews-container'),  # Тут будуть відображатись відгуки

    # Форма для додавання відгуку
    html.Div(id='review-input-section'),  # Покажемо форму лише якщо користувач залогінений

    html.A('Назад до карти', href='/', className='back-link')
])


# Сторінка реєстрації
register_layout = html.Div([
    html.Div(className="login-container", children=[
        html.H2("Реєстрація", className="login-title"),
        dcc.Input(id="reg-username", type="text", placeholder="Ім'я користувача", className="input-box"),
        dcc.Input(id="reg-email", type="email", placeholder="Email", className="input-box"),
        dcc.Input(id="reg-password", type="password", placeholder="Пароль", className="input-box"),
        html.Button("Зареєструватись", id="register-button", n_clicks=0, className="login-button"),
        html.Div(id="register-output"),  # Теж просто контейнер без класу
        html.A("Назад до мапи", href="/", className="back-link"),
        html.A("Вже зареєстровані? Натисніть сюди", href="/login", className="back-link")
    ])
], className="main-container")
# register_layout = html.Div([
#     html.Div(className="login-container", children=[
#         html.H2("Реєстрація", className="login-title"),
#         dcc.Input(id="reg-username", type="text", placeholder="Ім'я користувача", className="input-box"),
#         dcc.Input(id="reg-email", type="email", placeholder="Email", className="input-box"),
#         dcc.Input(id="reg-password", type="password", placeholder="Пароль", className="input-box"),
#         html.Button("Зареєструватись", id="register-button", n_clicks=0, className="login-button"),
#         html.Div(id="register-output", className="error-message"),
#         html.A("Назад до мапи", href="/", className="back-link"),
#         html.A("Вже зареєстровані? Натисніть сюди", href="/login", className="back-link")
#     ])
# ], className="main-container")
