import time
import csv
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#"new hampshire"

states = ["alabama", "alaska", "arizona", "arkansas", "california", "colorado",
            "connecticut", "delaware", "florida", "georgia", "hawaii", "idaho", 
            "illinois", "indiana", "iowa", "kansas", "kentucky", "louisiana", 
            "maine", "maryland", "massachusetts", "michigan", "minnesota",
            "mississippi","missouri", "montana", "nebraska", "nevada",
            "new hampshire", "new jersey", "new mexico", "new york", 
            "north carolina", "north dakota", "ohio", "oklahoma", "oregon", 
            "pennsylvania", "rhode island", "south carolina", "south dakota",
            "tennessee", "texas", "utah", "vermont", "virginia", "washington",
            "west virginia", "wisconsin", "wyoming", "district-of-columbia"]

def extract_hospital_data(hospital_div):
    hospital_name = hospital_div.find('div', {'data-field': '@title'}).span.text.strip()
    location = hospital_div.find('span', {'data-field': '@location'}).span.text.strip()
    distance = hospital_div.find('span', {'data-field': '@sldistance'}).span.text.strip()

    return {
        'name': hospital_name,
        'location': location,
        'distance': distance
    }




def get_data_for_state(driver, state):
    url = f"https://www.intuitive.com/en-us/provider-locator?location={state.replace(' ', '%20')}&search=hospitals&distance=500&specialty=all&procedure=all"
    driver.get(url)

    extracted_data = []

    while True:
        # Wait for the page to load
        time.sleep(1)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        hospitals = soup.find_all('div', class_='coveo-result-row')

        for hospital in hospitals:
            extracted_data.append(extract_hospital_data(hospital))

#        try:
#             # Wait for the dialog to appear and close it
#             dialog = WebDriverWait(driver, 10).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='dialog']"))
#             )
#             close_button = dialog.find_element_by_css_selector("button[aria-label='Close']")
#             close_button.click()
#         except TimeoutException:
#             # The dialog did not appear within 10 seconds, proceed
#             pass

#         try:
#             next_button = driver.find_element_by_css_selector("li.coveo-pager-next")
#             if "coveo-disabled" in next_button.get_attribute("class"):
#                 break
#             next_button.click()
#             time.sleep(2)
#         except NoSuchElementException:
#             break

         # Try to click the "Next" button
        try:
            next_button = driver.find_element(By.XPATH, "//li[@aria-label='Next']")
            if 'coveo-disabled' in next_button.get_attribute('class'):
                # If the "Next" button is disabled, we've reached the last page
                break
            else:
                driver.execute_script("arguments[0].click();", next_button)
        except NoSuchElementException:
            # If the "Next" button is not found, we've reached the last page
            break

    return extracted_data


def main():
    service = ChromeService(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    # Create a CSV file in the same location as the Python script
    script_dir = os.path.dirname(os.path.realpath(__file__))
    csv_file_path = os.path.join(script_dir, 'hospital_data_2.csv')
    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['State', 'Hospital Name', 'Location', 'Distance'])

        for state in states:
            state_data = get_data_for_state(driver, state)

            for hospital in state_data:
                csv_writer.writerow([state, hospital['name'], hospital['location'], hospital['distance']])
                print(f"Saved {hospital['name']} from {state}")

    driver.quit()

if __name__ == "__main__":
    main()



