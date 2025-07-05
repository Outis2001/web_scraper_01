from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

import time
import pandas as pd

service = Service(executable_path="./chromedriver-win64/chromedriver.exe")
driver = webdriver.Chrome(service=service)

url = "https://rainbowpages.lk"
driver.get(url)

WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "thumb"))
)