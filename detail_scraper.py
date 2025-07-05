from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

import time
import pandas as pd

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

# driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

from selenium.webdriver.chrome.service import Service
service = Service(executable_path="./chromedriver-win64/chromedriver.exe")
driver = webdriver.Chrome(service=service)

first_time = time.time()

final_list = []

def get_details(url, count):
    temp_list = []
    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "listing-profile-heading-wrapper"))
        )
    except TimeoutException:
        driver.refresh()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "listing-profile-heading-wrapper"))
        )

    try:
        name = driver.find_elements(By.ID, "listing-profile-heading")
        temp_list.append(name[0].text)
        print(name[0].text)
    except Exception as e:
        temp_list.append(None)
        print("No name found")

    try:
        address = driver.find_elements(By.CLASS_NAME, "col-md-10")
        temp_list.append(address[0].text)
        # print(address[0].text)
    except Exception as e:
        temp_list.append(None)
        print("No address found")

    try:
        email = driver.find_elements(By.CLASS_NAME, "col-md-11")
        temp_list.append(email[0].text)
        # print(email[0].text)
    except Exception as e:
        temp_list.append(None)
        print("No email found")

    try:
        contact_numbers = driver.find_elements(By.CLASS_NAME, "col-md-4")
        temp_list.append(contact_numbers[2].text.split(','))
        # print(contact_numbers[2].text)
    except Exception as e:
        temp_list.append(None)
        print("No contact numbers found")

    try:
        domain_name = driver.find_elements(By.CLASS_NAME, "col-md-8")
        temp_list.append(domain_name[2].text)
        # print(domain_name[2].text)
    except Exception as e:
        temp_list.append(None)
        print("No domain name found")

    try:
        lists = driver.find_elements(By.CLASS_NAME, "company-service")
        print(len(lists))
        if len(lists) == 0:
            temp_list.append(None)
            temp_list.append(None)
        elif len(lists) == 1:
            temp_list.append(lists[0].text.split('\n')[1:])
            temp_list.append(None)
        else:
            temp_list.append(lists[0].text.split('\n')[1:])
            temp_list.append(lists[1].text.split('\n')[1:])
    except Exception as e:
        temp_list.append(None)
        temp_list.append(None)
        print("No listed under found")

    final_list.append(temp_list)

csv_name = "All_links"
link_df = pd.read_csv(f"../Datasets/scraper_02/links/{csv_name}.csv")

lower_limit = 44179
url_list = link_df['business_link'].tolist()[lower_limit:]

count = lower_limit+1
temp_time = first_time
try:
    for url_link in url_list:
        print(f"Count: {count}")
        get_details(url_link, count)
        count += 1
        if count%300==0:
            df = pd.DataFrame(final_list, columns=["Company_Name", "Address", "Email", "Contact_Number", "Domain_Name", "Listed_Under", "Products_Services"])
            df.to_csv(f"../Datasets/scraper_02/details/{csv_name}_{lower_limit}_to_{count}.csv", index=False, header=True)
            print(time.time()-temp_time)
            temp_time = time.time()
except Exception as e:
    df = pd.DataFrame(final_list, columns=["Company_Name", "Address", "Email", "Contact_Number", "Domain_Name", "Listed_Under", "Products_Services"])
    df.to_csv(f"../Datasets/scraper_02/details/{csv_name}_{lower_limit}_to_{count}.csv", index=False, header=True)

df = pd.DataFrame(final_list, columns=["Company_Name", "Address", "Email", "Contact_Number", "Domain_Name", "Listed_Under", "Products_Services"])
df.to_csv(f"../Datasets/scraper_02/details/{csv_name}_{lower_limit}_to_{len(link_df['business_link'].tolist())}.csv", index=False, header=True)

driver.quit()

print(time.time() - first_time)