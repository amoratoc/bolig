from utils.dk_eng_dict import DK_ENG_dictionary
from utils.various import hash_str, find_nearest_stations, haversine_distance
from utils.features_to_parse import features
from databases.kbh import metro_train
import csv
import os
import requests
from bs4 import BeautifulSoup
import urllib.parse
import pandas as pd
from pathlib import Path
from geopy.geocoders import ArcGIS


CLASS_GRID_ITEM = "css-13jvjkd"
URL_PREFIX = "https://www.boligportal.dk"
URL = "https://www.boligportal.dk/lejligheder,huse/københavn/"


class BoligportalScrapper:

    @classmethod
    def update_apts_list(cls, csv_file_path: str | Path = None):

        # Read the existing file or create an empty dataframe
        if csv_file_path is not None and os.path.exists(csv_file_path):
            existing_list = pd.read_csv(csv_file_path)

        # Empty list to append all apartments
        all_apts = []

        # Create list of urls (main page does not load all apartments)
        page=123
        all_urls = [URL] + [URL + f"?offset={18*i}" for i in range(1, 123)]

        # Iterate through all the urls.
        for i, url in enumerate(all_urls):
            print(f"Parsing page {i}")
            url = urllib.parse.unquote(url)

            # Download the page content with the requests library
            html = requests.get(url).content

            # Parse the HTML content with the bs4 library
            soup = BeautifulSoup(html, 'html.parser')

            # Find the products that are in anchor "a" elements with class "CLASS_GRID_ITEM"
            all_a = soup.find_all('a', {"class": CLASS_GRID_ITEM})

            # Get the coordinates of all stations
            stations_coords = cls.read_stations_coords()

            # we loop through the apartments, and add each product's data as a dict object
            for a in all_a:
                # price_div = a.find_parent('div').find(name="div", attrs={"class": "css-dlcfcd"})
                #
                # div = a.find(name="div", string="DKK")

                string_to_hash = a.text.strip() + urllib.parse.unquote(a["href"])
                new_apt = {
                    "hash": hash_str(string_to_hash),
                    "name": a.text.strip(),
                    "url": URL_PREFIX + urllib.parse.unquote(a["href"])
                }

                # condition_to_add = csv_file_path is not None and not existing_list['hash'].eq(new_apt["hash"]).any()
                # if csv_file_path is None or condition_to_add:
                features_dict = cls.get_apt_features(new_apt["url"], stations_coords)
                new_apt.update(features_dict)
                all_apts.append(new_apt)

                # else:
                #     print("Not adding appartment")

        df = pd.DataFrame(all_apts)
        df.to_csv('./files/all_apts.csv', index=False)

        return all_apts

    @staticmethod
    def read_stations_coords() -> list:
        stations_coords = []
        for feature in metro_train["features"]:
            coords = feature["geometry"]["coordinates"][0]
            stations_coords.append(
                {
                 "coords": {"lat": coords[1], "lon": coords[0]},
                 "type": feature["properties"]["objekt_type"],
                 "name": feature["properties"]["navn"],
                 "kommune": feature["properties"]["kommune"],
                }
            )
        return stations_coords

    @staticmethod
    def str_to_float(string: str) -> float:
        return float(string
                     .strip()
                     .replace(" kr.", "")
                     .replace(".", "")
                     .replace(",", "")
                     )

    @classmethod
    def parse_utilities_price(cls, soup_apt) -> float:
        # Find element with "Månedlig aconto" and get its sibiling
        try:
            div = soup_apt.find(name="div", string="Månedlig aconto").find_next_sibling()
            # find the span and make it a number
            return cls.str_to_float(div.find(name="span").get_text())

        except AttributeError:
            return 0

    @classmethod
    def parse_move_in_price(cls, soup_apt) -> float:
        # Find element with "" and get its sibiling
        div = soup_apt.find(name="div", string="Indflytningspris").find_next_sibling()
        # find the span and make it a number
        return cls.str_to_float(div.find(name="span").get_text())

    @staticmethod
    def parse_apt_details(soup_apt) -> dict:
        # find section
        section_apt_details = soup_apt.find("h2", string="Detaljer om bolig").parent

        # Get all the properties as they share class names
        all_atrs = section_apt_details.find_all(name="span", attrs={"class": "css-1td16zm"})
        all_atrs_keys = [atr.text for atr in all_atrs]

        # Get all values of the properties as they share class names
        all_vals = section_apt_details.find_all(name="span", attrs={"class": "css-1f8murc"})
        all_atrs_vals = [atr.text for atr in all_vals]

        dict = {}
        for i, (atr, val) in enumerate(zip(all_atrs_keys, all_atrs_vals)):
            if atr == "Værelser":
                val = int(val.replace(".", ""))
            if atr == "Størrelse":
                val = float(val.replace(" m²", ""))
            dict[DK_ENG_dictionary[atr]] = val

        return dict

    @staticmethod
    def find_street_coords(street: str, postal_code: str, neighborhood: str, city: str, ):
        # Initialize the geolocator
        geolocator = ArcGIS()
        # build of the street
        street_name = street + ", " + postal_code + " " + neighborhood + ", " + city
        # Geocode the street name
        location = geolocator.geocode(street_name)
        return location.latitude, location.longitude

    @classmethod
    def get_apt_features(cls, apt_url: str, stations_coords: list | None = None):
        html_apt = requests.get(apt_url).content
        soup_apt = BeautifulSoup(html_apt, 'html.parser')

        apt_features = {}
        # Address
        location_div = soup_apt.find("div", {"class": "css-1gjufnd"})
        location_text = location_div.find(name="div").get_text().split(", ")
        apt_features["street"] = location_text[0].strip()
        apt_features["postal_code"] = int(location_text[1].split(" ")[0].strip())
        apt_features["city"] = location_text[1].split(" ")[1].strip()
        apt_features["neighborhood"] = location_text[2].split(" - ")[0].strip()

        # Apartment properties
        apt_features["description"] = soup_apt.find("div", {"class":"css-1j674uz"}).get_text()
        apt_features["price"] = cls.str_to_float(soup_apt.find("span", {"class": "css-1fhvb05"}).get_text())
        apt_features["utilities_price"] = cls.parse_utilities_price(soup_apt)
        apt_features["moving_in_price"] = cls.parse_move_in_price(soup_apt)

        # Apartment details
        apt_details = cls.parse_apt_details(soup_apt)
        apt_features.update(apt_details)

        if stations_coords:
            # Apartment location
            lat, lon = cls.find_street_coords(
                street=apt_features["street"],
                postal_code=str(apt_features["postal_code"]),
                neighborhood=apt_features["neighborhood"],
                city=apt_features["city"]
            )
            apt_features["latitude"] = lat
            apt_features["longitude"] = lon

            nearest_metro, distance_to_nearest_metro, nearest_s_station, distance_to_s_station = find_nearest_stations(
                [lat, lon], stations_coords)
            apt_features["nearest_metro"] = nearest_metro["name"]
            apt_features["distance_to_nearest_metro"] = distance_to_nearest_metro
            apt_features["nearest_s_station"] = nearest_s_station["name"]
            apt_features["distance_to_s_station"] = distance_to_s_station

        return apt_features

if __name__ == '__main__':
    # Create the .csv with the list of apts with their title and url
    all_apts = BoligportalScrapper.update_apts_list(csv_file_path="./files/all_apts.csv")

    coords_from = [55.71135, 12.569385]
    coords_to = [55.707877, 12.570332]
    dist = haversine_distance(coords_from[0], coords_from[1], coords_to[0], coords_to[1])


    # new = df[
    #     # (df["price"] < 15000) &
    #     # (df["rooms"] > 1) &
    #     # (df["neighborhood"] == "København Ø")
    #     (df["distance_to_nearest_metro"]>5)
    # ]
    #
    # url = new["url"].values[0]

    print("end")

