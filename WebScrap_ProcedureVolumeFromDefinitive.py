import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

from selenium.common.exceptions import ElementClickInterceptedException


# Constants
USERNAME = "nskerpon@its.jnj.com"
PASSWORD = "Happy@2022"

#CPT code on the left of the first page

CPT_CODES1 = ["43774","43886","43887","43888","44320","44345","44346","44340",
              "44322","44188","44206","44208","45805","45825","45563","44141",
              "44146","44143","44144","57307","45395","49591","49593","49594",
              "49615","49592","49595","49613","49614","11042","11043","15734",
              "50220","50225","50230","50234","50236","50240","57288"]

#CPT code on the right of the first page
CPT_CODES2 = ['44140','44145','44150','44204','49491','49505','49560','44950',
              '49650','49568','47562','47600','47605','47612','47630','58180',
              '44979','44960','44970','44160','43644','49651','49652','50280',
              '43846','43842','50300','50542','55840','55845','58150','58200',
              '58210','58240','58260','58262','58263','58267','58270','58275',
              '58280','58285','58290','58291','58292','58294','58152']
     
# Diagnosis
ICDs = ['K82.0', 'K82.1', '0DQ10ZZ', '0DQ14ZZ', '0DQ11ZZ', '0DQ12ZZ',
            '0DQ14ZZ', '0DVB0ZZ', '0DVU4ZZ', '0UDB0ZZ', '0DVU0ZZ', '0TC10ZZ',
            '0TC14ZZ', '0SB00ZZ', 'N32.81', '0DV14ZZ']

# Initialize the web driver
driver = webdriver.Chrome(executable_path='/Users/t.l./Downloads/chromedriver')
driver.get("https://sts.defhc.com/Account/Login?Username=nskerpon@its.jnj.com")

# Log in
def login(driver):
    driver.get("https://sts.defhc.com/Account/Login?Username=nskerpon@its.jnj.com")
    password_field = driver.find_element(By.ID, "Password")
    password_field.send_keys(PASSWORD)
    login_button = driver.find_element(By.XPATH, "//button[@value='Log in']")
    login_button.click()
    # Wait for login to complete
    WebDriverWait(driver, 10).until(EC.url_contains("https://www.defhc.com/"))


login(driver)

# Loop through the years and CPT/ICD codes
for icd_code in ICDs: # change the names
    for year in range(2017, 2024):
        # Go to the ASCProcedureAnalyticsFirstPage
        driver.get(f"https://www.defhc.com/surgerycenters/ASCDiagnosisAnalyticsProvider?claim_year={year}&icd_ten_dx_code={icd_code}&zip_code_radius=%20&report=ASCDiagnosisAnalyticsProvider&xx_resultRoute=ASCDiagnosisAnalyticsFirstPage&%24origin=ASCDiagnosisAnalyticsFirstPage")
        # Procedure websites
        # https://www.defhc.com/hospitals/HospitalInpatientProcedureAnalyticsProviderCommercial?claim_year={year}&cpt_code={cpt_code}&zip_code_radius=%20&xx_resultRoute=HospitalInpatientProcedureAnalyticsProvider&report=HospitalInpatientProcedureAnalyticsProviderCommercial&%24origin=HospitalInpatientProcedureAnalyticsProviderCommercial
        # https://www.defhc.com/surgerycenters/ASCProcedureAnalyticsFirstPage?claim_year={year}&CPT_CODE={cpt_code}&zip_code_radius=%20&report=ASCProcedureAnalyticsProvider&xx_resultRoute=ASCProcedureAnalyticsFirstPage&%24origin=ASCProcedureAnalyticsFirstPage")
        # https://www.defhc.com/hospitals/HospitalOutpatientProcedureAnalyticsProviderCommercial?claim_year={year}&cpt_code={cpt_code}&zip_code_radius=%20&report=HospitalOutpatientProcedureAnalyticsProviderCommercial&xx_resultRoute=HospitalOutpatientProcedureAnalyticsFirstPageCommercial&%24origin=HospitalOutpatientProcedureAnalyticsFirstPageCommercial
        # https://www.defhc.com/physicians/PhysicianProcedureAnalyticsPhysician?claim_year={year}&cpt_code={cpt_code}&zip_code_radius=%20&report=PhysicianProcedureAnalyticsPhysician&xx_resultRoute=PhysicianProcedureAnalyticsFirstPage&%24origin=PhysicianProcedureAnalyticsFirstPage
        # https://www.defhc.com/physgroups/PhysicianGroupProcedureAnalyticsProvider?claim_year=2023&cpt_code=44774&zip_code_radius=%20&report=PhysicianGroupProcedureAnalyticsProvider&xx_resultRoute=PhysicianGroupProcedureAnalyticsFirstPage&%24origin=PhysicianGroupProcedureAnalyticsFirstPage
        # Diagnosis websites
        # https://www.defhc.com/surgerycenters/ASCDiagnosisAnalyticsProvider?claim_year={year}&icd_ten_dx_code={icd_code}&zip_code_radius=%20&report=ASCDiagnosisAnalyticsProvider&xx_resultRoute=ASCDiagnosisAnalyticsFirstPage&%24origin=ASCDiagnosisAnalyticsFirstPage
        if "https://sts.defhc.com/Account/Login" in driver.current_url:
            print("Session expired. Logging in again...")
            login(driver)
        
        wait = WebDriverWait(driver, 40)
        wait.until(EC.presence_of_element_located((By.ID, "dhc-product-suite-iframe")))

        driver.switch_to.frame("dhc-product-suite-iframe")

        # Check for no results
        no_results = driver.find_elements(By.XPATH, "//span[contains(text(), 'Your search returned 0 results.')]")
        if no_results:
            print(f"No results found for year {year} and code {icd_code}. Skipping...")
            time.sleep(1)
            continue
        
        # Download the Excel file
        export_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.hideInPrint.dhc-gridview-export")))
        export_button.click()

        # Select the export option
        export_select = wait.until(EC.presence_of_element_located((By.ID, "MainContent_MainContent_ProductPageContent_AnalyticsResultRightPanel_GridviewExportHyperLink1_ExportPreset")))
        select = Select(export_select)
        select.select_by_visible_text("Export ASC Diagnoses by Provider (Commercial Claims)") # change the correct name

        # Click the export button (need to confirm manually sometimes)
        export_confirm_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='button' and contains(@class, 'btn-export')]")))
        try:
        # Attempt to click using the previous code
            export_confirm_button.click()
        except ElementClickInterceptedException:
            # If not clickable, use JavaScript to click on the element
            driver.execute_script("arguments[0].click();", export_confirm_button)

        # Enter the export name 
        driver.switch_to.default_content()
        export_name_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="exportName"]')))
        
        export_name_input.clear()
        export_name_input.send_keys(f"ASC_{year}_{icd_code}") # change the file name

        # Click the final export button
        final_export_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='button' and contains(@class, 'ms-Button--primary') and not(contains(@class, 'is-disabled'))]")))
        final_export_button.click()

        # Wait for the "Download here" button and click it
        download_here_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='button' and contains(@class, 'ms-Button') and .//span[contains(text(), 'Download here')]]")))
        download_here_button.click()



        # Wait for the file to download
        time.sleep(2)

        if "https://sts.defhc.com/Account/Login" in driver.current_url:
            print("Session expired. Logging in again...")
            login(driver)

# Close the browser
driver.quit()
