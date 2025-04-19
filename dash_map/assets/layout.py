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

index_page = html.Div([
    html.H1("Мапа укриттів", className='page-title'),

    html.Div([
        dcc.Input(
            id='address-input',
            type='text',
            placeholder='Введіть адресу (наприклад: Вулиця Зелена 20А)',
            className='input-box',
            debounce=True
        ),
        html.Button('Знайти укриття', id='find-route-btn-main', n_clicks=0, className='search-button'),
        html.Div(id='search-status', className='status-message')
    ], className='search-container'),

    html.Div(id='route-message', className='status-message'),  # ✅ Додано контейнер для повідомлень

    html.Div([
        dcc.Link('Логін', href='/login', className='button-link'),
        html.Br(),
        dcc.Link('Реєстрація', href='/register', className='button-link')
    ], className='button-container'),

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

login_layout = html.Div([
    html.Div(className="login-container", children=[
        html.H2("Логін", className="login-title"),
        dcc.Input(id="login-email", type="email", placeholder="Email", className="input-box"),
        dcc.Input(id="login-password", type="password", placeholder="Пароль", className="input-box"),
        html.Button("Увійти", id="login-button", n_clicks=0, className="login-button"),
        html.Div(id="login-output", className="error-message"),
        html.A("Назад до мапи", href="/map", className="back-link"),
        html.A("Ще не зареєструвались? Натисніть сюди", href="/register", className="back-link")
    ])
], className="main-container")

# Додамо нову сторінку для відгуків
page_3_layout = html.Div([
    html.H1("Відгуки про укриття"),
    html.Div(id='reviews-container'),  # Тут будуть відображатись відгуки

    # Форма для додавання відгуку
    dcc.Input(id='new-review', type='text', placeholder='Ваш відгук...', className='input-box'),
    html.Button('Лишити відгук', id='submit-review', n_clicks=0, className='submit-button'),

    html.A('Назад до карти', href='/', className='back-link')
])



register_layout = html.Div([
    html.Div(className="login-container", children=[
        html.H2("Реєстрація", className="login-title"),
        dcc.Input(id="reg-username", type="text", placeholder="Ім'я користувача", className="input-box"),
        dcc.Input(id="reg-email", type="email", placeholder="Email", className="input-box"),
        dcc.Input(id="reg-password", type="password", placeholder="Пароль", className="input-box"),
        html.Button("Зареєструватись", id="register-button", n_clicks=0, className="login-button"),
        html.Div(id="register-output", className="error-message"),
        html.A("Назад до мапи", href="/", className="back-link"),
        html.A("Вже зареєстровані? Натисніть сюди", href="/login", className="back-link")
    ])
], className="main-container")
