# add the imports for web scraping
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
url_base = 'https://www.redfin.com/city'

# write a function that takes a path such as '/8903/TX/Houston', builds a URL from the base, and returns the HTML

# Class Selectors by Data Point
# Price: .homecardV2Price
# Address: .homeAddressV2
# Beds: .HomeStatsV2 .stats:nth-of-type(1)
# Baths: .HomeStatsV2 .stats:nth-of-type(2)
# Sqft: .HomeStatsV2 .stats:nth-of-type(3)
# First Image URL: .homecard-image:nth-of-type(1)


def get_page(path):
    url = url_base + path
    driver.get(url)
    html = driver.page_source
    return html

# For each of the selectors defined, write a function that takes the HTML and returns the data point


def get_price(html):
    soup = BeautifulSoup(html, 'html.parser')
    price = soup.select('.homecardV2Price')
    return price[0].text


def get_address(html):
    soup = BeautifulSoup(html, 'html.parser')
    address = soup.select('.homeAddressV2')
    return address[0].text


def get_beds(html):
    soup = BeautifulSoup(html, 'html.parser')
    beds = soup.select('.HomeStatsV2 .stats:nth-of-type(1)')
    return beds[0].text


def get_baths(html):
    soup = BeautifulSoup(html, 'html.parser')
    baths = soup.select('.HomeStatsV2 .stats:nth-of-type(2)')
    return baths[0].text


def get_sqft(html):
    soup = BeautifulSoup(html, 'html.parser')
    sqft = soup.select('.HomeStatsV2 .stats:nth-of-type(3)')
    return sqft[0].text


def get_image(html):
    soup = BeautifulSoup(html, 'html.parser')
    image = soup.select('.homecard-image:nth-of-type(1)')
    return image[0]['src']

# Write a function that loops over all .HomeCard elements and calls the functions above to get the data for each listing


def get_listings(html):
    soup = BeautifulSoup(html, 'html.parser')
    print(soup)
    listings = soup.select('.HomeCard')
    for listing in listings:
        price = get_price(str(listing))
        address = get_address(str(listing))
        beds = get_beds(str(listing))
        baths = get_baths(str(listing))
        sqft = get_sqft(str(listing))
        image = get_image(str(listing))
        print(price, address, beds, baths, sqft, image)


def init():
    # get the HTML for the page
    html = get_page('/8903/TX/Houston')
    # get the listings
    get_listings(html)


init()
