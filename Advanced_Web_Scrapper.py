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
    EC.presence_of_element_located((By.CLASS_NAME, "category-item"))
)

categories = driver.find_elements(By.CLASS_NAME, "category-item")
# category_names = [category.text for category in categories]  # Store category names separately

# from below list you can choose from what categories you want names
# category_names = ['Advertising', 'Agriculture', 'Banking', 'Beauty Culture', 'Computers', 'Constructions',
#                   'Education', 'Electrical', 'Embassies', 'Emergency', 'Entertainment', 'Essential Services',
#                   'Financing', 'Food', 'Government', 'Hardware', 'Health', 'Home', 'Hotels', 'Industrial', 'Insurance',
#                   'Interior', 'Media', 'Office', 'Other', 'Professional Services', 'Religious', 'Repair',
#                   'Shopping', 'Short Codes', 'Sport', 'Telecommunication', 'Transport', 'Travel', 'Vehicle', 'Weddings']
category_names = ['Other']


def remove_bad_links(link_urls):
    bad_links = ["https://rainbowpages.lk/", "https://rainbowpages.lk/merchant/login.php",
                     "https://rainbowpages.lk/merchant/register.php", "https://rainbowpages.lk/",
                     "https://rainbowpages.lk/about.php",
                     "https://rainbowpages.lk/products.php", "https://rainbowpages.lk/advertise.php",
                     "https://rainbowpages.lk/news.php", "https://rainbowpages.lk/contact-us.php",
                     "https://rainbowpages.lk/personal-names.php", "https://rainbowpages.lk/advertising/",
                     'https://rainbowpages.lk/agriculture/', 'https://rainbowpages.lk/baby-goods/',
                     'https://rainbowpages.lk/banking/', 'https://rainbowpages.lk/beauty-culture/',
                     'https://rainbowpages.lk/computers/', 'https://rainbowpages.lk/constructions/',
                     'https://rainbowpages.lk/education/', 'https://rainbowpages.lk/electrical/',
                     'https://rainbowpages.lk/embassies/', 'https://rainbowpages.lk/emergency/',
                     'https://rainbowpages.lk/entertainment/', 'https://rainbowpages.lk/essential-services/',
                     'https://rainbowpages.lk/financing/', 'https://rainbowpages.lk/food/',
                     'https://rainbowpages.lk/government/', 'https://rainbowpages.lk/hardware/',
                     'https://rainbowpages.lk/health/', 'https://rainbowpages.lk/home/',
                     'https://rainbowpages.lk/hotels/', 'https://rainbowpages.lk/industrial/',
                     'https://rainbowpages.lk/insurance/', 'https://rainbowpages.lk/interior/',
                     'https://rainbowpages.lk/media/', 'https://rainbowpages.lk/office/',
                     'https://rainbowpages.lk/other/', 'https://rainbowpages.lk/pets/',
                     'https://rainbowpages.lk/professional-services/', 'https://rainbowpages.lk/religious/',
                     'https://rainbowpages.lk/repair/', 'https://rainbowpages.lk/shopping/',
                     'https://rainbowpages.lk/short-codes/', 'https://rainbowpages.lk/sport/',
                     'https://rainbowpages.lk/telecommunication/', 'https://rainbowpages.lk/transport/',
                     'https://rainbowpages.lk/travel/', 'https://rainbowpages.lk/vehicle/',
                     'https://rainbowpages.lk/weddings/', 'https://rainbowpages.lk/privacy-policy-mobile.php',
                     'http://www.weddingdirectory.lk/', 'http://www.touristdirectory.lk/',
                     'https://www.facebook.com/RainbowPages.lk', 'https://twitter.com/rainbowpageslk',
                     'https://www.linkedin.com/company/rainbowpages', 'https://www.youtube.com/c/SLTRainbowpageslk',
                     'https://www.instagram.com/sltrainbowpages/', 'http://www.slt.lk/', 'http://beyondm.net/']

    # Exclude unnecessary links using above bad_links array
    for k in bad_links:
        while (k in link_urls):
            link_urls.remove(k)

    return link_urls

sub_categories = []
previous_href = ""
for category_name in category_names:
    names = []
    print(category_name + "\n")
    try:
        # Navigate to the category page
        driver.get(f"https://rainbowpages.lk/{category_name}")
        # Wait for the links to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "a"))
        )

        # Extract all links
        links = driver.find_elements(By.TAG_NAME, "a")
        link_urls = [link.get_attribute("href") for link in links if link.get_attribute("href")]
        link_urls = remove_bad_links(link_urls)

        new_elements = []
        print(new_elements)
        # Visit each link
        for link in link_urls:
            try:
                print(link + " : " + category_name)
                driver.get(link)  # Navigate to the link
                time.sleep(3)  # Allow some time for the page to load
                # Wait for the links to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.TAG_NAME, "a"))
                )
            except Exception as e:
                print(f"Error visiting {link}: {e}")

            # Go through all pages
            while (len(driver.find_elements(By.CLASS_NAME, "media-heading")) > 0):
                elements = driver.find_elements(By.TAG_NAME, "a")

                for element in elements:
                    check_link = element.get_attribute("href")
                    if ((link in check_link) and (not (check_link in new_elements))):
                        if (("page" not in str(check_link.split('/')[5])) and ("#" not in str(check_link))):
                            new_elements.append(check_link)
                            # get_details(check_link)

                try:
                    # Wait for the next button link to be present
                    next_button = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//a[@aria-label="Next"]'))
                    )
                    # Get the next button attribute
                    href_value = next_button.get_attribute("href")

                    # If the next button link equals to the previous next button link then break the loop
                    if href_value == previous_href:
                        break
                    # If the next button link not equals to the previous next button link plus # then click the next button
                    elif href_value != previous_href + "#":
                        next_button.click()
                        previous_href = href_value
                    else:
                        break
                    print(f"The href value is: {href_value}")
                except Exception as e:
                    print(f"Error retrieving href: {e}")

            df = pd.DataFrame(new_elements, columns=["business_link"])
            # df.to_csv(f"../Datasets/scraper_02/links/{category_name}.csv", index=False)
            df.to_csv(f"{category_name}.csv", index=False)

        # Go back to the main page
        driver.back()
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "category-item"))
        )

    except Exception as e:
        print(f"Error navigating to {category_name}: {e}")

time.sleep(3)

driver.quit()