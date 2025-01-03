from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

service = Service(executable_path="./chromedriver-win64/chromedriver.exe")
driver = webdriver.Chrome(service=service)

driver.get("https://rainbowpages.lk/")

WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "category-item"))
)

categories = driver.find_elements(By.CLASS_NAME, "category-item")
category_names = [category.text for category in categories]  # Store category names separately

sub_categories = []
for category_name in category_names:
    try:
        # Navigate to the category page
        driver.get(f"https://rainbowpages.lk/{category_name}")
        sub_cats = driver.find_elements(By.CLASS_NAME, "category-title")
        sub_cats_links = driver.find_elements(By.TAG_NAME, "a")
        sub_category_names = [sub_cats_link.text for sub_cats_link in sub_cats_links]  # Store sub category names separately
        sub_categories.append(sub_category_names)
        # Go back to the main page
        driver.back()
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "category-item"))
        )
    except Exception as e:
        print(f"Error navigating to {category_name}: {e}")

time.sleep(3)
driver.quit()

print(sub_categories)