import csv
import requests
from bs4 import BeautifulSoup
import urllib.parse
import pandas as pd

# we store the URL we're scraping in a variable
# url = "https://www.jofogas.hu/magyarorszag/muszaki-cikkek-elektronika"
url = "https://www.boligportal.dk/lejeboliger/københavn/"

# we download the page conent with the requests library
html = requests.get(url).content

# we parse the HTML content with the bs4 library
soup = BeautifulSoup(html, 'html.parser')

# we find the products using the "list-item" class
# all_divs = soup.find_all('div', { "class": "temporaryFlexColumnClassName css-nkly31" })   #css-bq36qw  css-7r8xmo
all_a = soup.find_all('a', {"class": "css-13jvjkd" })

# we define the result variable
all_apts = []
# we loop through the products, and add each product's data
# as a dict object
for a in all_a:
    all_apts.append({
        "name": a.text.strip(),
        "url": "https://www.boligportal.dk" + urllib.parse.unquote(a["href"])
    })


cols = [
    "street",
    "postal_code",
    "city",
    "neighborhood",
    "type",
    "description",
    "price",
    "utilities_price",
    "moving_in_price",
    "type",
    "area",
    "rooms",
    "floor",
    "furnished",
    "sharing friendly",
    "pets allowed",
    "Elevator",
    "senior friendly",
    "only students",
    "balcony/terrace",
    "parking",
    "dishwasher",
    "washing maching",
    "charging stand",
    "dryer",
    "energy label"
]
apt_db = pd.DataFrame(columns=cols)


def parse_utilities_price(soup_apt) -> float:
    # Find element with "Månedlig aconto" and get its sibiling
    try:
        div = soup_apt.find(name="div", string="Månedlig aconto").find_next_sibling()
        # find the span and make it a number
        return float(div.find(name="span").get_text()
                     .replace(" kr.", "")
                     .replace(".", ""))
    except AttributeError:
        return 0


def parse_move_in_price(soup_apt) -> float:
    # Find element with "" and get its sibiling
    div = soup_apt.find(name="div", string="Indflytningspris").find_next_sibling()
    # find the span and make it a number
    return float(div.find(name="span").get_text()
                 .replace(" kr.", "")
                 .replace(".", ""))

dictionary = {
    "Boligtype": "type",
    "Størrelse": "area",
    "Værelser": "rooms",
    "Etage": "floor",
    "Møbleret": "furnished",
    "Delevenlig": "sharing friendly",
    "Husdyr tilladt": "pets allowed",
    "Elevator": "Elevator",
    "Seniorvenlig": "senior friendly",
    "Kun for studerende": "only students",
    "Altan/terrasse": "balcony/terrace",
    "Parkering": "parking",
    "Opvaskemaskine": "dishwasher",
    "Vaskemaskine": "washing maching",
    "Ladestander": "charging stand",
    "Tørretumbler": "dryer",
    "Energimærke": "energy label"
}

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
        dict[dictionary[atr]] = val

    return dict


for i, apt in enumerate(all_apts):
    html_apt = requests.get(apt['url']).content
    soup_apt = BeautifulSoup(html_apt, 'html.parser')

    # Address
    location_div = soup_apt.find("div", {"class": "css-1gjufnd"})
    location_text = location_div.find(name="div").get_text().split(", ")
    apt_db.at[i, "street"] = location_text[0].strip()
    apt_db.at[i, "postal_code"] = int(location_text[1].split(" ")[0].strip())
    apt_db.at[i, "city"] = location_text[1].split(" ")[1].strip()
    apt_db.at[i, "neighborhood"] = location_text[2].split(" - ")[0].strip()

    # Apartment properties
    apt_db.at[i, "description"] = soup_apt.find("div", {"class": "css-1j674uz"}).get_text()
    apt_db.at[i, "price"] = float(soup_apt.find("span", {"class": "css-1fhvb05"}).get_text().replace(".",""))
    apt_db.at[i, "utilities_price"] = parse_utilities_price(soup_apt)
    apt_db.at[i, "moving_in_price"] = parse_move_in_price(soup_apt)

    details_dict = parse_apt_details(soup_apt)
    for key, val in details_dict.items():
        apt_db.at[i, key] = val


from .databases.kbh import kbh
kbh = kbh

# i=0
# apt = all_apts[0]
print("end")



new = apt_db[(apt_db["price"]<15000) & (apt_db["rooms"]>1)]

if __name__ == '__main__':
    print('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
