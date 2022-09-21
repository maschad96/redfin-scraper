import inquirer
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
url_base = 'https://www.redfin.com'

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
    if price:
        # remove commas
        return price[0].text.replace(',', '')
    else:
        return 'N/A'


def get_address(html):
    soup = BeautifulSoup(html, 'html.parser')
    address = soup.select('.homeAddressV2')
    if address:
        return address[0].text.replace(',', '')
    else:
        return 'N/A'


def get_beds(html):
    soup = BeautifulSoup(html, 'html.parser')
    beds = soup.select('.HomeStatsV2 .stats:nth-of-type(1)')
    if beds:
        return beds[0].text.replace(' Beds', '')
    else:
        return 'N/A'


def get_baths(html):
    soup = BeautifulSoup(html, 'html.parser')
    baths = soup.select('.HomeStatsV2 .stats:nth-of-type(2)')
    if baths:
        return baths[0].text.replace(' Baths', '')
    else:
        return 'N/A'


def get_sqft(html):
    soup = BeautifulSoup(html, 'html.parser')
    sqft = soup.select('.HomeStatsV2 .stats:nth-of-type(3)')
    if sqft:
        return sqft[0].text.replace(',', '').replace(' Sq. Ft.', '')
    else:
        return 'N/A'


def get_image(html):
    soup = BeautifulSoup(html, 'html.parser')
    image = soup.select('.slider-item:nth-of-type(1) .homecard-image')
    # if image[0].get('src') evaluates to None, then return N/A
    if image:
        if image[0].get('src'):
            return image[0].get('src')
        else:
            return 'N/A'
    else:
        return 'N/A'


def get_property_url(html):
    soup = BeautifulSoup(html, 'html.parser')
    link = soup.select('.homeAddressV2 + script + a')
    if link:
        if link[0].get('href'):
            return 'https://www.redfin.com' + link[0].get('href')
        else:
            return 'N/A'
    else:
        return 'N/A'

# Write a function that loops over all .HomeCard elements and calls the functions above to get the data for each listing


def get_listings(html):
    soup = BeautifulSoup(html, 'html.parser')
    listings = soup.select('.HomeCard')
    listings_array = []
    for index, listing in enumerate(listings):
        price = get_price(str(listing))
        address = get_address(str(listing))
        beds = get_beds(str(listing))
        baths = get_baths(str(listing))
        sqft = get_sqft(str(listing))
        image = get_image(str(listing))
        url = get_property_url(str(listing))
        if index % 2 == 0:
            driver.execute_script("window.scrollBy(0, 350)")
        listings_array.append([price, address, beds, baths, sqft, url])
    return listings_array


def convert_to_k(num):
    # convert num to int
    num = int(num)
    num = num / 1000
    num = str(num) + 'k'
    return num


def create_filter_query_string(beds, baths, min_price, max_price, min_sqft, max_sqft, property_type, remarks, page):
    filter_string = f'/filter/min-beds={beds},max-beds={beds},min-baths={baths},min-price={convert_to_k(min_price)},max-price={convert_to_k(max_price)},min-sqft={convert_to_k(min_sqft)}-sqft,max-sqft={convert_to_k(max_sqft)}-sqft,property-type={property_type},remarks={remarks}/page-{page}'
    return filter_string


def prompt_property_type():
    questions = [
        inquirer.Confirm('house', message='House?', default=True),
        inquirer.Confirm('condo', message='Condo?', default=True),
        inquirer.Confirm('townhouse', message='Townhouse?', default=True),
    ]
    answers = inquirer.prompt(questions)
    property_types = []

    if answers['house']:
        property_types.append('house')
    if answers['condo']:
        property_types.append('condo')
    if answers['townhouse']:
        property_types.append('townhouse')

    property_types_string = '+'.join(property_types)
    return property_types_string


def prompt_remarks():
    return input('Enter any keywords, separated by commas')


def write_to_csv_file(listings):
    with open('./listings.csv', 'w') as f:
        f.write('Price,Address,Beds,Baths,Sqft,URL\n')
        for listing in listings:
            print(listing)
            f.write(','.join(listing) + '\n')


def scrape_with_args(beds, baths, min_price, max_price, min_sqft, max_sqft, property_type, remarks, paginated_listings, page=1):
    # create a filter using create_filter_query_string
    filter = create_filter_query_string(
        beds, baths, min_price, max_price, min_sqft, max_sqft, property_type, remarks, page)
    print(page)
    path_with_filter = '/city/10201/NV/Las-Vegas' + filter
    print(path_with_filter)
    html = get_page(path_with_filter)
    soup = BeautifulSoup(html, 'html.parser')
    has_paginate_button = soup.select(
        'button[data-rf-test-id="react-data-paginate-next"]')
    # get the listings
    listings = get_listings(html)
    # push and flatten the listings to paginated_listings
    paginated_listings.extend(listings)
    if (has_paginate_button):
        page += 1
        scrape_with_args(beds, baths, min_price, max_price, min_sqft,
                         max_sqft, property_type, remarks, paginated_listings, page)
    else:
        write_to_csv_file(paginated_listings)
        return driver.close()


def init(paginated_listings=[]):
    beds = input('Enter the number of beds: ')
    baths = input('Enter the number of baths: ')
    min_price = input('Enter the minimum price: ')
    max_price = input('Enter the maximum price: ')
    min_sqft = input('Enter the minimum square footage: ')
    max_sqft = input('Enter the maximum square footage: ')
    # create a prompt with a radio option for the 'property-type'
    property_type = prompt_property_type()
    remarks = prompt_remarks()
    scrape_with_args(beds, baths, min_price, max_price, min_sqft,
                     max_sqft, property_type, remarks, paginated_listings)


init()
