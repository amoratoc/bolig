import csv
import requests
from bs4 import BeautifulSoup

# we store the URL we're scraping in a variable
# url = "https://www.jofogas.hu/magyarorszag/muszaki-cikkek-elektronika"
url = "https://www.boligportal.dk/lejeboliger/københavn/"

# we download the page conent with the requests library
html = requests.get(url).content

# we parse the HTML content with the bs4 library
soup = BeautifulSoup(html)

# we find the products using the "list-item" class
termekek = soup.find_all('div', { "class": "css-7r8xmo" })
all_divs = soup.find_all('div')

# we define the result variable
results = []
# we loop through the products, and add each product's data
# as a dict object
for termek in termekek:
    results.append({
        "name": termek.find("h3", { "class": "item-title" }).text.strip(),
        "price": termek.find("span", { "class": "price-value" }).text.strip(),
    })

if __name__ == '__main__':
    print('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
