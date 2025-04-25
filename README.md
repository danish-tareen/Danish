# Danish
Scrape Yellow pages with Python Script 



from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import time
import random

def split_name(full_name):
    names = full_name.split()
    first_name = names[0] if len(names) > 0 else 'N/A'
    last_name = names[1] if len(names) > 1 else 'N/A'
    return first_name, last_name

def parse_address(full_address):
    address_parts = full_address.split(', ')
    street = address_parts[0] if len(address_parts) > 0 else 'N/A'
    suite = address_parts[1] if len(address_parts) > 1 else 'N/A'
    zip_code = address_parts[-1] if len(address_parts) > 2 else 'N/A'
    return street, suite, zip_code

data = []

for page_number in range(1, 15):  # Specify your page range
    target_website = f"https://www.yellowpages.com/search?search_terms=Real%20Estate%20and%20Property%20Management&geo_location_terms=New%20York%2C%20NY&page={page_number}"
    print(f"\nFetching data from page {page_number}")

    driver = webdriver.Chrome()
    driver.get(target_website)
    time.sleep(random.uniform(2, 6))

    try:
        allResults = driver.find_elements(By.CLASS_NAME, "result")

        for result in allResults:
            obj = {}

            try:
                full_name = result.find_element(By.CLASS_NAME, "business-name").text
                first_name, last_name = split_name(full_name)
                obj["FirstName"] = first_name
                obj["LastName"] = last_name
            except:
                obj["FirstName"] = 'N/A'
                obj["LastName"] = 'N/A'

            try:
                obj["phoneNumber"] = result.find_element(By.CLASS_NAME, "phones").text
            except:
                obj["phoneNumber"] = 'N/A'

            try:
                full_address = result.find_element(By.CLASS_NAME, "adr").text
                obj["FullAddress"] = full_address
                street, suite, zip_code = parse_address(full_address)
                obj["Street"] = street
                obj["ZIP Code"] = zip_code
            except:
                obj["FullAddress"] = 'N/A'
                obj["Street"] = 'N/A'
                obj["ZIP Code"] = 'N/A'

            try:
                obj["BusinessCategory"] = result.find_element(By.CLASS_NAME, "categories").text
            except:
                obj["BusinessCategory"] = 'N/A'

            try:
                element = result.find_element(By.CLASS_NAME, "business-name")
                lateral_string = element.get_attribute("href")

                if not lateral_string:
                    raise Exception("Empty href found")

                if lateral_string.startswith('https://www.yellowpages.com'):
                    full_href = lateral_string
                else:
                    full_href = 'https://www.yellowpages.com' + lateral_string

                obj["FullHref"] = full_href

                driver.execute_script("window.open(arguments[0]);", full_href)
                driver.switch_to.window(driver.window_handles[1])
                time.sleep(random.uniform(2, 6))

                try:
                    obj["Website"] = driver.find_element(By.CSS_SELECTOR, "p.website a").get_attribute("href")
                except:
                    obj["Website"] = 'N/A'

                try:
                    obj["Email"] = driver.find_element(By.CLASS_NAME, "email-business").get_attribute('href').replace("mailto:", "")
                except:
                    obj["Email"] = 'N/A'

                driver.close()
                driver.switch_to.window(driver.window_handles[0])
            except Exception as e:
                print(f"Error while fetching details: {e}")
                obj["FullHref"] = 'N/A'
                obj["Website"] = 'N/A'
                obj["Email"] = 'N/A'

            data.append(obj)

    except Exception as e:
        print(f"Error fetching data from page {page_number}: {e}")

    driver.quit()
    print("Waiting for 45 seconds before fetching the next page...")
    time.sleep(45)

df = pd.DataFrame(data, columns=["FirstName", "LastName", "phoneNumber", "FullAddress", "Street", "ZIP Code", "BusinessCategory", "FullHref", "Website", "Email"])
df.to_excel("Businesses_Real_Estate_4_pages.xlsx", index=False)

print("✅ Data extraction complete.")
