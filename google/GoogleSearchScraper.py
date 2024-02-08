import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from multiprocessing import Pool
import time

def check_for_captcha(driver):
    try:
        element_recaptcha = driver.find_element(By.ID, 'recaptcha')
        return True
    except:
        return False

def perform_google_search(query, proxy_info, offset_x=50):
    #proxy = proxy_info.split(":")[0]
    #port = int(proxy_info.split(":")[1])

    # Set up proxy options for Chrome webdriver
    # chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument('--proxy-server=http://{}:{}'.format(proxy, port))

    # Create the Chrome webdriver with options
    driver = webdriver.Chrome(executable_path='D:\chromedriver\chromedriver.exe') # options=chrome_options

    try:
        # Get the current window position
        window_x = driver.execute_script("return window.screenX;")
        window_y = driver.execute_script("return window.screenY;")

        # Set the new window position with the horizontal offset
        driver.set_window_position(window_x + offset_x, window_y)

        driver.get('https://www.google.com')

        # Check for captcha and wait until it disappears
        while check_for_captcha(driver):
            print("Captcha detected. Sleeping for 1 second.")
            time.sleep(1)

        search = driver.find_element("name", "q")
        search.send_keys(query)
        search.submit()

        results = []
        page = 1

        while True:
            # Check for captcha and wait until it disappears
            while check_for_captcha(driver):
                print("Captcha detected. Sleeping for 1 second.")
                time.sleep(1)

            # Find search results
            search_results = driver.find_elements(By.CSS_SELECTOR, '.tF2Cxc')
            if not search_results:
                print("No more search result pages.")
                break

            for result in search_results:
                link = result.find_element(By.CSS_SELECTOR, '.yuRUbf a').get_attribute('href')
                results.append(link)

            # Check if the "Next" button is present and wait for captcha if needed
            try:
                next_button = driver.find_element(By.ID, 'pnnext')
                next_button.click()
                page += 1
                time.sleep(2.4)
            except:
                if check_for_captcha(driver):
                    continue
                print("No more search result pages.")
                break

        return results

    finally:
        driver.quit()

if __name__ == "__main__":
    search_queries = [
        "site:docs.google.com poetry",
        "site:docs.google.com journal",
        "site:docs.google.com notes",
        "site:docs.google.com survey results",
        "site:docs.google.com meeting notes",
        "site:docs.google.com financial plan",
        "site:docs.google.com marketing campaign",
        "site:docs.google.com business proposal",
        "site:docs.google.com client presentation",
        "site:docs.google.com research proposal"
        # Add more queries here as needed
    ]

    proxies = [
        "p.webshare.io:9999"
        # Add more proxies to the list as needed
    ]

    # Use multiprocessing to run searches in parallel
    with Pool(processes=len(search_queries)) as pool:
        search_results = pool.starmap(perform_google_search, [(query, proxy) for query in search_queries for proxy in proxies])

    # Create the directory if it doesn't exist
    if not os.path.exists('rawLinks'):
        os.makedirs('rawLinks')

    # Save the results to separate files in the "rawLinks" directory
    for i, results in enumerate(search_results):
        with open(f'rawLinks/GdocURLs_{i}.txt', 'w') as file:
            for link in results:
                file.write(link + '\n')

    print("Searches completed. Links saved to separate files in the 'rawLinks' directory.")
