import os
import osmnx as ox
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import heapq

GRAPH_FILE = "lviv_graph.graphml"

def load_graph():
    if os.path.exists(GRAPH_FILE):
        return ox.load_graphml(GRAPH_FILE)
    G = ox.graph_from_place("Lviv, Ukraine", network_type="drive", simplify=True)
    G = ox.simplify_graph(G)
    ox.save_graphml(G, GRAPH_FILE)
    return G

def find_user_location(address):
    geolocator = Nominatim(user_agent="shelter_finder")
    location = geolocator.geocode(address)
    if location is None:
        return None
    return (location.latitude, location.longitude)

def parse_shelters(file_path, user_point):
    shelters = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        next(file)
        for line in file:
            data = line.strip().split(',')
            if len(data) >= 10 and data[-2] and data[-1]:
                shelter_coords = (float(data[-2]), float(data[-1]))
                if 0.2 <= geodesic(user_point, shelter_coords).km <= 1:
                    shelters[f"{data[7]} {data[8]}"] = shelter_coords
    return shelters

def build_graph_dict(G):
    graph_dict = {node: {} for node in G.nodes()}
    for u, v, data in G.edges(data=True):
        length = data.get("length", float('inf'))
        graph_dict[u][v] = length
    return graph_dict

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

def compute_route(address, shelter_file):
    G = load_graph()
    user_point = find_user_location(address)
    if user_point is None:
        return None, None, None
    user_node = ox.distance.nearest_nodes(G, user_point[1], user_point[0])
    
    shelters = parse_shelters(shelter_file, user_point)
    if not shelters:
        return None, None, None

    shelter_nodes = {
        name: ox.distance.nearest_nodes(G, coords[1], coords[0])
        for name, coords in shelters.items()
    }

    graph_dict = build_graph_dict(G)
    distances, prev_nodes = dijkstra(graph_dict, user_node)
    closest_name, closest_node = min(shelter_nodes.items(), key=lambda item: distances[item[1]])

    path = []
    while closest_node is not None:
        path.append(closest_node)
        closest_node = prev_nodes.get(closest_node)
    path = path[::-1]
    route_coords = [(G.nodes[n]["y"], G.nodes[n]["x"]) for n in path]
    length = sum(graph_dict[path[i]][path[i+1]] for i in range(len(path)-1))
    time_minutes = round((length / 1000) / 5 * 60, 1)

    return closest_name, time_minutes, route_coords
