states = ["alabama", "alaska", "arizona", "arkansas", "california", "colorado",
            "connecticut", "delaware", "florida", "georgia", "hawaii", "idaho", 
            "illinois", "indiana", "iowa", "kansas", "kentucky", "louisiana", 
            "maine", "maryland", "massachusetts", "michigan", "minnesota",
            "mississippi", "missouri", "montana", "nebraska", "nevada",
            "new mpshire", "new jersey", "new mexico", "new york", 
            "north carolina", "north dakota", "ohio", "oklahoma", "oregon", 
            "pennsylvania", "rhode island", "south carolina", "south dakota",
            "tennessee", "texas", "utah", "vermont", "virginia", "washington",
            "west virginia", "wisconsin", "wyoming"]  # Add more states as needed

import time
import csv
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException



def extract_hospital_data(hospital_div):
    hospital_name = hospital_div.find('div', {'data-field': '@title'}).span.text.strip()
    location = hospital_div.find('span', {'data-field': '@location'}).span.text.strip()
    distance = hospital_div.find('span', {'data-field': '@sldistance'}).span.text.strip()

    return {
        'name': hospital_name,
        'location': location,
        'distance': distance
    }

import csv
from time import sleep
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

# function to get data for a state
def get_data_for_state(driver, state):
    print(f"Fetching data for {state}...")
    driver.get(f"https://www.avvo.com/search/lawyer_search?utf8=%E2%9C%93&q=&loc={state}&start=0")
    sleep(3)
    try:
        # click on the cookie consent banner if it is present
        cookie_banner = driver.find_element_by_css_selector('#onetrust-accept-btn-handler')
        cookie_banner.click()
    except NoSuchElementException:
        pass

    # loop through all pages for the state
    page_num = 1
    while True:
        print(f"Processing page {page_num}...")
        # get the lawyer listings
        listings = driver.find_elements_by_css_selector('.lawyer-search-results .lawyer-search-result')

        # loop through the listings and extract data
        for listing in listings:
            name = listing.find_element_by_css_selector('.lawyer-search-result-name a').text
            rating = listing.find_element_by_css_selector('.lawyer-search-result-rating').get_attribute('title')
            reviews = listing.find_element_by_css_selector('.lawyer-search-result-reviews a').text
            practice_areas = ", ".join([area.text for area in listing.find_elements_by_css_selector('.lawyer-search-result-practice-area a')])
            city = listing.find_element_by_css_selector('.lawyer-search-result-location').text

            # write data to CSV file
            with open(f"{state}.csv", mode='a') as csv_file:
                fieldnames = ['Name', 'Rating', 'Reviews', 'Practice Areas', 'City']
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                writer.writerow({'Name': name, 'Rating': rating, 'Reviews': reviews, 'Practice Areas': practice_areas, 'City': city})

        # check if there is a next page button
        try:
            obstructing_element_selector = '.onetrust-consent-sdk'
            obstructing_element = driver.find_element_by_css_selector(obstructing_element_selector)
            driver.execute_script("arguments[0].style.display = 'none';", obstructing_element)
            
            next_button = driver.find_element_by_css_selector('.coveo-pager-next')
            driver.execute_script("arguments[0].click();", next_button)
        except NoSuchElementException:
            print(f"Finished processing all pages for {state}.")
            break

        page_num += 1

# create a new Chrome driver
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)


def get_data_for_state(driver, state):
    url = f"https://www.intuitive.com/en-us/provider-locator?location={state.replace(' ', '%20')}&search=hospitals&distance=500&specialty=all&procedure=all"
    driver.get(url)

    # Wait for the page to load
    time.sleep(5)

    while True:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        hospitals = soup.find_all('div', class_='coveo-result-row')

        extracted_data = []
        for hospital in hospitals:
            extracted_data.append(extract_hospital_data(hospital))

        # Save extracted_data to CSV
        with open('hospital_data.csv', 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['name', 'location', 'distance']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            for data in extracted_data:
                writer.writerow(data)

        # Check for next page and click the button if it exists
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, '.coveo-pager-next')
            if 'coveo-disabled' in next_button.get_attribute('class'):
                break

            # Wait for the obstructing element to be hidden or removed
            obstructing_element_selector = 'div[role="dialog"][aria-describedby="onetrust-policy-text"]'
            
            WebDriverWait(driver, 10).until(
                EC.invisibility_of_element_located((By.CSS_SELECTOR, obstructing_element_selector))
            )

            next_button.click()
            time.sleep(3)

        except NoSuchElementException:
            break

if __name__ == "__main__":
    # Setup Chrome driver
    driver = webdriver.Chrome(ChromeDriverManager().install())

    # Create a CSV file with headers
    with open('hospital_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['name', 'location', 'distance']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

    # Fetch data for each state
    for state in states:
        print(f"Fetching data for {state}...")
        get_data_for_state(driver, state)

    driver.quit()

