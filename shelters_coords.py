"""shelters_coords"""
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

def get_coordinates(address) -> tuple[int, int] | None:
    """Gets the latitude and longitude from the address"""
    geolocator = Nominatim(user_agent="shelter_locator")
    try:
        location = geolocator.geocode(address, timeout=10)
        if location:
            return location.latitude, location.longitude
    except GeocoderTimedOut:
        return None, None
    return None, None

def add_coordinates_to_file(input_file:str, output_file:str) -> None:
    """Creates a new file with coordinates of every shelter"""
    df = pd.read_csv(input_file)

    df["latitude"] = None
    df["longitude"] = None
    i = 1
    for index, row in df.iterrows():
        print(i)
        i += 1
        if row["city"] != "Львів":
            continue
        address = f"{row['street']} {row['building_number']}, \
Львів, {row['district']}, Львівська область, Україна"
        lat, lon = get_coordinates(address)
        df.at[index, "latitude"] = lat
        df.at[index, "longitude"] = lon


    df.to_csv(output_file, index=False)

if __name__ == "__main__":
    add_coordinates_to_file("ukrittya_lviv_obl.csv", "shelters_coords.csv")
