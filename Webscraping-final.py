from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv

# Set up the driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Open CSV file for writing
with open('water_data.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    # Write header
    writer.writerow([
        "Year", "Month", "Rainfall", "Inflow From Other States", "Ground Water", 
        "Soil Moisture", "Reservoir", "Major", "Medium", "MI Tanks", 
        "Evapotranspiration", "Outflow", "River", "Micro Basin", 
        "Consumption", "Irrigation", "Industry", "Domestic", 
        "Surface and SubSurface Outflow"
    ])

    # Loop through each year and month from 2021 to 2024
    for year in range(2021, 2025):
        for month in range(1, 13):
            start_date = f"{year}{month:02d}01"
            end_date = f"{year}{month:02d}{31 if month != 2 else 28}"

            # Construct the URL with the updated startDate and endDate
            url = f"https://apwrims.ap.gov.in/mis/wa/summary?sourceOfData=AWS&locationHierarchy=ADMIN&locationLevel=DISTRICT&startDate={start_date}&endDate={end_date}&cType=MANDAL&pType=DISTRICT&timePeriod=custom&hierarchyId=WA_ADMIN&module=wa&location=AP%23%236f86292b-dd9a-4987-bb8f-c3940263b349%26Ananthapuramu%23%2323bdafe5-1283-4cbe-8813-d419fcccb535&componentName=default"

            driver.get(url)

            # Wait for the page to load
            time.sleep(5)

            # Extract data using XPaths and CSS Selectors
            try:
                rainfall = driver.find_element(By.XPATH, "//tr[td[contains(text(),'Rainfall')]]/td[2]").text
                inflow_other_states = driver.find_element(By.XPATH, "//tr[td[contains(text(),'Inflow From Other States')]]/td[2]").text
                ground_water = driver.find_element(By.XPATH, "//tr[td[contains(text(),'Ground Water')]]/td[2]").text
                soil_moisture = driver.find_element(By.XPATH, "//tr[td[contains(text(),'Soil Moisture (till 150 cm depth)')]]/td[2]").text
                reservoir = driver.find_element(By.XPATH, "//tr[td[contains(text(),'Reservoir')]]/td[2]").text
                major = driver.find_element(By.XPATH, "//tr[td[contains(text(),'Major')]]/td[2]").text
                medium = driver.find_element(By.XPATH, "//tr[td[contains(text(),'Medium')]]/td[2]").text
                mi_tanks = driver.find_element(By.XPATH, "//tr[td[contains(text(),'MI Tanks (Geotagged)')]]/td[2]").text
                evapotranspiration = driver.find_element(By.XPATH, "//tr[td[contains(text(),'Evapo-transpiration')]]/td[2]").text
                outflow = driver.find_element(By.XPATH, "//tr[td[contains(text(),'Outflow')]]/td[2]").text
                river = driver.find_element(By.XPATH, "//tr[td[contains(text(),'River')]]/td[2]").text
                micro_basin = driver.find_element(By.XPATH, "//tr[td[contains(text(),'Micro Basin')]]/td[2]").text
                consumption = driver.find_element(By.XPATH, "//tr[td[contains(text(),'Consumption')]]/td[2]").text
                irrigation = driver.find_element(By.XPATH, "//tr[td[contains(text(),'Irrigation')]]/td[2]").text
                industry = driver.find_element(By.XPATH, "//tr[td[contains(text(),'Industry')]]/td[2]").text
                domestic = driver.find_element(By.XPATH, "//tr[td[contains(text(),'Domestic')]]/td[2]").text
                surface_subsurface_outflow = driver.find_element(By.XPATH, "//tr[td[contains(text(),'Surface and SubSurface Outflow')]]/td[2]").text

                # Write the data row into CSV
                writer.writerow([
                    year, month, rainfall, inflow_other_states, ground_water, 
                    soil_moisture, reservoir, major, medium, mi_tanks, 
                    evapotranspiration, outflow, river, micro_basin, 
                    consumption, irrigation, industry, domestic, 
                    surface_subsurface_outflow
                ])
            except Exception as e:
                print(f"Error while processing {start_date} to {end_date}: {e}")

# Close the driver
driver.quit()
