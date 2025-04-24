import os
import osmnx as ox
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import heapq

GRAPH_FILE = "lviv_graph.graphml"

# Завантаження графу Львову
def load_graph():
    if os.path.exists(GRAPH_FILE):
        return ox.load_graphml(GRAPH_FILE)
    G = ox.graph_from_place("Lviv, Ukraine", network_type="drive", simplify=True)
    G = ox.simplify_graph(G)
    ox.save_graphml(G, GRAPH_FILE)
    return G


# Шукаєм поточне місцезнаходження користувача у координатах широти та довготи
def find_user_location(address, city="Львів", country="Україна"):
    geolocator = Nominatim(user_agent="shelter_finder", timeout=10)
    full_address = f"{address}, {city}, {country}"
    location = geolocator.geocode(full_address)
    if location is None:
        return None
    return (location.latitude, location.longitude)

# Берем до уваги тільки укриття які не дальше ніж 1 км від нас
def parse_shelters(file_path, user_point):
    shelters = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        next(file)
        for line in file:
            data = line.strip().split(',')
            if len(data) >= 10 and data[-2] and data[-1]:
                shelter_coords = (float(data[-2]), float(data[-1]))
                if geodesic(user_point, shelter_coords).km <= 1:
                    shelters[f"{data[7]} {data[8]}"] = shelter_coords
    return shelters


# Будуємо граф
def build_graph_dict(G):
    graph_dict = {node: {} for node in G.nodes()}
    for u, v, data in G.edges(data=True):
        length = data.get("length", float('inf'))
        graph_dict[u][v] = length
    return graph_dict

# Реалізація алгоритму Дейкстри
def dijkstra(graph, start_point):
    shortest_paths = {node: float('inf') for node in graph}
    pre = {node: None for node in graph}
    shortest_paths[start_point] = 0
    heap = [(0, start_point)]
    visited = set()
    while heap:
        current_distance, current = heapq.heappop(heap)
        if current in visited:
            continue
        visited.add(current)
        for neighbor, weight in graph[current].items():
            if neighbor not in visited:
                new_distance = current_distance + weight
                if new_distance < shortest_paths[neighbor]:
                    shortest_paths[neighbor] = new_distance
                    pre[neighbor] = current
                    heapq.heappush(heap, (new_distance, neighbor))
    return shortest_paths, pre


# Шукаєм найкоротший шлях
def compute_route(address, shelter_file):
    G = load_graph()
    user_point = find_user_location(address)
    if user_point is None:
        return None, None, None
    try:
        user_node = ox.distance.nearest_nodes(G, user_point[1], user_point[0])
    except Exception as e:
        print("Помилка при визначенні вузла для користувача:", e)
        return None, None, None
    
    shelters = parse_shelters(shelter_file, user_point)
    if not shelters:
        return None, None, None

    shelter_nodes = {}
    node_to_shelter_name = {}
    for name, coords in shelters.items():
        try:
            node = ox.distance.nearest_nodes(G, coords[1], coords[0])
            shelter_nodes[name] = node
            node_to_shelter_name[node] = name
        except Exception:
            continue

    graph_dict = build_graph_dict(G)
    distances, prev_nodes = dijkstra(graph_dict, user_node)

    reachable_shelters = {
        name: node for name, node in shelter_nodes.items()
        if distances.get(node, float('inf')) != float('inf')
    }

    if reachable_shelters:
        closest_name, closest_node = min(
            reachable_shelters.items(), key=lambda item: distances[item[1]]
        )
        path = []
        current = closest_node
        while current is not None:
            path.append(current)
            current = prev_nodes.get(current)
        path = path[::-1]

        route_coords = [(G.nodes[n]["y"], G.nodes[n]["x"]) for n in path]

        # Якщо маршрут має лише одну точку — будуємо пряму лінію
        if len(route_coords) < 2:
            # Знаходимо shelter з мінімальною геодезичною відстанню
            closest_name, shelter_coords = min(
                shelters.items(),
                key=lambda item: geodesic(user_point, item[1]).meters
            )
            route_coords = [user_point, shelter_coords]
            distance_m = geodesic(user_point, shelter_coords).meters
            time_minutes = round((distance_m / 1000) / 5 * 60, 1)
            return closest_name + " (дуже близько)", time_minutes, route_coords


        length = sum(graph_dict[path[i]][path[i+1]] for i in range(len(path)-1))
        time_minutes = round((length / 1000) / 5 * 60, 1)

        return closest_name, time_minutes, route_coords
