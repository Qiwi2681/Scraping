import time
import csv
import driver_manager as driver_manager
import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import exceptions as se
from bs4 import BeautifulSoup

login_url = 'https://steamcommunity.com/login/home/'

LowLiqStickers = [
    r'https://steamcommunity.com/market/listings/730/Sticker%20%7C%20Keoz%20%7C%20Rio%202022',
    r'https://steamcommunity.com/market/listings/730/Sticker%20%7C%20acoR%20%7C%20Rio%202022',
]
highliqstickers = [
    r'https://steamcommunity.com/market/listings/730/Sticker%20%7C%20Grim%20%7C%20Antwerp%202022',
    r'https://steamcommunity.com/market/listings/730/Sticker%20%7C%20es3tag%20%7C%20Antwerp%202022',
    r'https://steamcommunity.com/market/listings/730/Sticker%20%7C%20TeSeS%20%7C%20Antwerp%202022',
    r'https://steamcommunity.com/market/listings/730/Sticker%20%7C%20sico%20%7C%20Antwerp%202022',
    r'https://steamcommunity.com/market/listings/730/Sticker%20%7C%20degster%20%7C%20Antwerp%202022'
]
highliqgraffities = [
    r'https://steamcommunity.com/market/listings/730/Sealed%20Graffiti%20%7C%20Lambda%20(Brick%20Red)',
    r'https://steamcommunity.com/market/listings/730/Sealed%20Graffiti%20%7C%20King%20Me%20(Monster%20Purple)',
]

drivers = driver_manager.ParallelDriverManager(threads=1)

def login(driver, cred):
    login = cred.split(':')
    driver.get(login_url)
    # Create a WebDriverWait instance
    wait = WebDriverWait(driver, 10) # Use WebDriverWait to wait for the input fields to be present
    input_fields = wait.until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "newlogindialog_TextInput_2eKVn"))
    )
    username = input_fields[0]
    password = input_fields[1]

    username.send_keys(login[0])
    password.send_keys(login[1])

    # Find and click the "Sign in" button by its CSS selector
    sign_in_button = driver.find_element(By.CSS_SELECTOR, ".newlogindialog_SubmitButton_2QgFE")
    sign_in_button.click()

    while(driver.current_url == login_url):
        time.sleep(1)

    return False

def extract_price(input_string):
    lines = input_string.split('\n')
    if len(lines) >= 2:
        try:
            currency, price = lines[1].split('$')
            price = price[1:]
        except ValueError:
            currency = lines[1][0]
            price = lines[1][1:]
        return price, currency
    return None

def scrape_market(driver):
    # Create a list to store item information
    names = []
    last_names = []

    while True:
        # Wait logic
        try:
            # for listing element
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "searchResultsRows"))
            )
            # for steam javascript
            WebDriverWait(driver, 10).until(
                lambda driver: driver.execute_script("return getComputedStyle(document.getElementById('searchResultsRows')).opacity === '1';")
            )
        except se.TimeoutException:
            driver.refresh()
            time.sleep(1)
            continue
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        # Find all the items in the HTML
        items = soup.find_all('div', {'class': 'market_listing_row market_recent_listing_row market_listing_searchresult'})

        # Iterate through the items and extract information
        temp_items = []
        for item in items:
            item_name = item.find('span', {'class': 'market_listing_item_name'}).text.strip()
            item_listing = item.find('span', {'class': 'market_listing_num_listings_qty'}).text.strip()
            item_price = item.find('span', {'class': 'normal_price'}).text.strip()
            item_price, currency = extract_price(item_price)
            temp_items.append([item_name, item_listing, item_price, currency])
        
        if not temp_items:
            driver.refresh()
            time.sleep(1)
            continue
        elif temp_items != last_names:
            last_names = temp_items
            for item in temp_items:
                item.append(datetime.datetime.now())
                names.append(item)
            temp_items = []
            

        end_element = soup.find('span', {'id': 'searchResults_end'})
        total_element = soup.find('span', {'id': 'searchResults_total'})

        if end_element and total_element:
            end = int(end_element.text.strip())
            total = int(total_element.text.strip())

            # Check if we have reached the last page
            if end == total:
                break

            url = driver.current_url
            if '#' in url:
                url, page = url.split('#')
                # Find the numeric part of the page string
                page_numeric = int(''.join(filter(str.isdigit, page)))
                # Increment the numeric part
                page_numeric += 1
                # Format the page string with the incremented numeric part
                page = f'#p{page_numeric}_price_asc'
                driver.get(url + page)
                time.sleep(1)
                continue
            else:
                driver.get(url + '#p1_price_asc')
                time.sleep(1)
                continue
        else:
            driver.refresh()
            continue

    return names

def scrape_item(driver):
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "hover_item_name"))
    )
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    if soup.find('div', {'class': 'market_listing_table_message'}).text.strip():
        while soup.find('div', {'class': 'market_listing_table_message'}).text.strip().startswith('There was an error'):
            driver.refresh()
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "hover_item_name"))
            )
            time.sleep(2)
            soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Find all the items in the HTML
    item_name = soup.find('h1', {'class': 'hover_item_name'}).text.strip()
    data = soup.find_all('span', {'class': 'market_commodity_orders_header_promote'})
    quantity = data[0].text.strip()
    price = data[1].text.strip()[4:]

    
    return [item_name, quantity, price]


class SteamBot():
    def __init__(self, creds:[str]):
        self.creds = creds
        self.threads = len(creds)
        self.driver_manager = driver_manager.ParallelDriverManager(threads=self.threads)

    def login(self):
        self.driver_manager.start_drivers()
        drivers = self.driver_manager.get_drivers()
        for i, driver in enumerate(drivers):
            login(driver, self.creds[i])

    def temp(self):
        urls = []
        with open('trolling_graffities.txt', 'r') as f:
            urls = f.readlines()
        return urls

    def scrape_item(self):
        self.driver_manager.populate_url_pool(self.temp())
        item_data = self.driver_manager.parallel_url_task(scrape_item)
        return item_data[0]

    def scrape_market(self, url):
        self.driver_manager.populate_url_pool([url])
        item_data = self.driver_manager.parallel_url_task(scrape_market)
        return item_data[0][0]


item_dict = {
    'trolling_graffities': {
        'url': 'https://steamcommunity.com/market/search?q=&category_730_ItemSet%5B%5D=any&category_730_ProPlayer%5B%5D=any&category_730_StickerCapsule%5B%5D=any&category_730_TournamentTeam%5B%5D=any&category_730_Weapon%5B%5D=any&category_730_SprayCapsule%5B%5D=tag_csgo_spray_std2_drops_2&appid=730',
        'filename': 'trolling_graffities.csv',
    },
    'collection2_graffities': {
        'url': 'https://steamcommunity.com/market/search?q=&category_730_ItemSet%5B%5D=any&category_730_ProPlayer%5B%5D=any&category_730_StickerCapsule%5B%5D=any&category_730_TournamentTeam%5B%5D=any&category_730_Weapon%5B%5D=any&category_730_SprayCapsule%5B%5D=tag_csgo_spray_std2_drops_1&appid=730',
        'filename': 'collection2_graffities.csv',
    },
    'collection3_graffities': {
        'url': 'https://steamcommunity.com/market/search?q=&category_730_ItemSet%5B%5D=any&category_730_ProPlayer%5B%5D=any&category_730_StickerCapsule%5B%5D=any&category_730_TournamentTeam%5B%5D=any&category_730_Weapon%5B%5D=any&category_730_SprayCapsule%5B%5D=tag_csgo_spray_std3_drops&appid=730',
        'filename': 'collection3_graffities.csv',
    },
    'berlin_stickers': {
        'url': 'https://steamcommunity.com/market/search?q=&category_730_ItemSet%5B%5D=any&category_730_ProPlayer%5B%5D=any&category_730_StickerCapsule%5B%5D=any&category_730_TournamentTeam%5B%5D=any&category_730_Weapon%5B%5D=any&category_730_StickerCategory%5B%5D=tag_PlayerSignature&category_730_StickerCategory%5B%5D=tag_TeamLogo&category_730_StickerCategory%5B%5D=tag_Tournament&category_730_Tournament%5B%5D=tag_Tournament16&appid=730',
        'filename': 'berlin_stickers.csv',
    },
    'rmr_stickers': {
        'url': 'https://steamcommunity.com/market/search?q=&category_730_ItemSet%5B%5D=any&category_730_ProPlayer%5B%5D=any&category_730_StickerCapsule%5B%5D=any&category_730_TournamentTeam%5B%5D=any&category_730_Weapon%5B%5D=any&category_730_StickerCategory%5B%5D=tag_PlayerSignature&category_730_StickerCategory%5B%5D=tag_TeamLogo&category_730_StickerCategory%5B%5D=tag_Tournament&category_730_Tournament%5B%5D=tag_Tournament17&appid=730',
        'filename': 'rmr_stickers.csv',
    },
    'stockholm_stickers': {
        'url': 'https://steamcommunity.com/market/search?q=&category_730_ItemSet%5B%5D=any&category_730_ProPlayer%5B%5D=any&category_730_StickerCapsule%5B%5D=any&category_730_TournamentTeam%5B%5D=any&category_730_Weapon%5B%5D=any&category_730_StickerCategory%5B%5D=tag_PlayerSignature&category_730_StickerCategory%5B%5D=tag_TeamLogo&category_730_StickerCategory%5B%5D=tag_Tournament&category_730_Tournament%5B%5D=tag_Tournament18&appid=730',
        'filename': 'stockholm_stickers.csv',
    },
    'rio_stickers': {
        'url': 'https://steamcommunity.com/market/search?q=&category_730_ItemSet%5B%5D=any&category_730_ProPlayer%5B%5D=any&category_730_StickerCapsule%5B%5D=any&category_730_TournamentTeam%5B%5D=any&category_730_Weapon%5B%5D=any&category_730_StickerCategory%5B%5D=tag_PlayerSignature&category_730_StickerCategory%5B%5D=tag_TeamLogo&category_730_StickerCategory%5B%5D=tag_Tournament&category_730_Tournament%5B%5D=tag_Tournament20&appid=730',
        'filename': 'rio_stickers.csv',
    },
    'antwerp_stickers': {
        'url': 'https://steamcommunity.com/market/search?q=&category_730_ItemSet%5B%5D=any&category_730_ProPlayer%5B%5D=any&category_730_StickerCapsule%5B%5D=any&category_730_TournamentTeam%5B%5D=any&category_730_Weapon%5B%5D=any&category_730_StickerCategory%5B%5D=tag_PlayerSignature&category_730_StickerCategory%5B%5D=tag_TeamLogo&category_730_StickerCategory%5B%5D=tag_Tournament&category_730_Tournament%5B%5D=tag_Tournament19&appid=730',
        'filename': 'antwerp_stickers.csv',
    },
    'paris_stickers': {
        'url': 'https://steamcommunity.com/market/search?q=&category_730_ItemSet%5B%5D=any&category_730_ProPlayer%5B%5D=any&category_730_StickerCapsule%5B%5D=any&category_730_TournamentTeam%5B%5D=any&category_730_Weapon%5B%5D=any&category_730_StickerCategory%5B%5D=tag_PlayerSignature&category_730_StickerCategory%5B%5D=tag_TeamLogo&category_730_StickerCategory%5B%5D=tag_Tournament&category_730_Tournament%5B%5D=tag_Tournament21&appid=730',
        'filename': 'paris_stickers.csv',
    }
}


if __name__ == '__main__':
    bots = ['username:password', 'User:Pass']
    for bot in bots:
        bot.login()


    item_data = bots.scrape_market(item_dict['trolling_graffities']['url'])


    ################ scrape_market parsing ################
    csv_file = item_dict['trolling_graffities']['filename']

    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)

        # Write the data rows
        for row in item_data:
            print(row)
            writer.writerow(row)


