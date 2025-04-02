import dash
import dash_leaflet as dl
from dash import html
import osmnx as ox
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import heapq
import os

GRAPH_FILE = "lviv_graph.graphml"
if os.path.exists(GRAPH_FILE):
    G = ox.load_graphml(GRAPH_FILE)
else:
    G = ox.graph_from_place("Lviv, Ukraine", network_type="drive", simplify=True)
    ox.save_graphml(G, GRAPH_FILE)


geolocator = Nominatim(user_agent="shelter_finder")
address = "Вулиця Степана Бандери, Львів"
location = geolocator.geocode(address)
user_point = (location.latitude, location.longitude)

user_node = ox.distance.nearest_nodes(G, user_point[1], user_point[0])
shelters = {}
with open('shelters_coords.csv', 'r', encoding='utf-8') as file:
    next(file) 
    for line in file:
        data = line.strip().split(',')
        if len(data) >= 10 and data[-2] and data[-1]:
            shelter_coords = (float(data[-2]), float(data[-1]))
            if geodesic(user_point, shelter_coords).km <= 0.5:
                shelters[f"{data[7]} {data[8]}"] = shelter_coords

graph_dict = {node: {} for node in G.nodes()}
for u, v, data in G.edges(data=True):
    length = data.get("length")
    graph_dict[u][v] = length

def dj(graph, start_point):
    """
    Алгоритм Дейкстри

    Args:
        graph (_type_): Граф Львову
        start_point (_type_): Адреса користувача

    Returns:
        _type_: Повертає шлях і відстань
    """
    shortest_paths = {node: float('inf') for node in graph}
    pre = {node: None for node in graph}
    shortest_paths[start_point] = 0
    visited = []
    heap = [(0, start_point)]
    while len(visited) < len(graph):
        if not heap:
            break
        current_distance, y = heapq.heappop(heap)
        if y in visited:
            continue
        visited.append(y)
        for neighbor, weight in graph[y].items():
            if neighbor not in visited:
                new_distance = current_distance + weight
                if new_distance < shortest_paths[neighbor]:
                    shortest_paths[neighbor] = new_distance
                    pre[neighbor] = y
                    heapq.heappush(heap, (new_distance, neighbor))
    return shortest_paths, pre

shelter_nodes = {name: ox.distance.nearest_nodes(G, coords[1], coords[0]) for name, coords in shelters.items()}
if not shelter_nodes:
    print("Не вдалося знайти укриттів в межах 500 м.")
else:
    distances, previous_nodes = dj(graph_dict, user_node)
    closest_shelter_name, shelter_node = min(
        shelter_nodes.items(),
        key=lambda item: distances[item[1]]
    )
    path = []
    while shelter_node is not None:
        path.append(shelter_node)
        shelter_node = previous_nodes.get(shelter_node)
    path = path[::-1]
    route_coords = [(G.nodes[node]["y"], G.nodes[node]["x"]) for node in path]

    app = dash.Dash(__name__)
    app.layout = html.Div([
        html.H4(f"Найближче укриття: {closest_shelter_name}"),
        dl.Map(style={'width': '100%', 'height': '500px'}, center=[49.8397, 24.0297], zoom=14, children=[
            dl.TileLayer(),
            dl.Polyline(positions=route_coords, color="red", weight=5),
            dl.Marker(
                position=route_coords[0],
                icon={"iconUrl": "https://maps.google.com/mapfiles/ms/icons/blue-dot.png"},
                children=dl.Tooltip("Старт")
            ),
            dl.Marker(
                position=route_coords[-1],
                icon={"iconUrl": "https://maps.google.com/mapfiles/ms/icons/red-dot.png"},
                children=dl.Tooltip("Укриття")
            )
        ])
    ])

    if __name__ == '__main__':
        app.run(debug=True)
