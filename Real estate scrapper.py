from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
import csv

chromeOptions = Options()
chromeOptions.add_argument("--kiosk")
PAGE_COUNT = int(input('Enter number of pages to be scraped: '))
driver = webdriver.Chrome(options=chromeOptions)
driver.get("https://www.99acres.com/")


driver.find_element(By.XPATH, '//input[@id="keyword2"]').click()
time.sleep(1)

driver.find_element(By.XPATH, '//div[@id="bedroom_num_wrap"]').click()
time.sleep(1)

driver.find_element(By.XPATH, '//div[@id="3"]').click()
time.sleep(1)

input_element = driver.find_element(By.XPATH, '//input[@id="keyword2"]')

input_element.clear()

input_element.send_keys("Bangalore")
time.sleep(1)

input_element.send_keys(Keys.RETURN)
time.sleep(3)

with open('apartments_listings.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['Name', 'Sq Ft', 'Price', 'Location']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    
    page_count = 0
    
    while page_count < PAGE_COUNT:
        
        last_height = driver.execute_script("return window.pageYOffset")
        scroll_increment = 200
        
        while True:
            driver.execute_script("window.scrollTo(0, {});".format(scroll_increment))
            time.sleep(1)
            
            new_height = driver.execute_script("return window.pageYOffset;")
            
            if new_height == last_height:
                break
            last_height = new_height
            
            scroll_increment = scroll_increment + 300
            
        next_page = driver.find_elements(By.XPATH, "//div[contains(@class, 'Pagination__srpPagination')]//a[contains(@class,'list_header_bold')]")[1]
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        items = soup.find_all('div', {'class': ['projectTuple__descCont', 'srpTuple__tupleDetails']})
        
        for item in items:
            apartment = {}

            if 'projectTuple__descCont' in item['class']:
                
                apartment['Name'] = item.find('a', {'class': 'projectTuple__projectName'}).text
                location_text = item.find('h2', {'class': 'projectTuple__subHeadingWrap'}).text
                apartment["Location"] = location_text.split(" in ")[-1]
                
                sqft = []
                prices = []

                prize_size_card = item.find_all('div', {'class': 'pageComponent configurationCards__configurationCardContainer'})
                
                for card in prize_size_card:
                    
                    try:
                        sqft_text = card.find('span', {'class': 'caption_subdued_medium configurationCards__cardAreaSubHeadingOne'}).text
                        sqft.append(sqft_text)
                    except AttributeError:
                        sqft.append("N/A")
                        
                    price_text = card.find('span', {'class': 'list_header_bold configurationCards__srpPriceHeading configurationCards__configurationCardsHeading'}).text
                    prices.append(price_text)

                    apartment["Sq Ft"] = ", ".join(sqft).replace("'", "")
                    apartment["Price"] = ", ".join(prices).replace("'", "")
                    
            else:
                apartment['Name'] = item.find('td', {'id': 'srp_tuple_society_heading'}).text
                location_text_2 = item.find('a', {'id': 'srp_tuple_property_title'}).text
                apartment["Location"] = location_text_2.split(" in ")[-1]
                apartment['Sq Ft'] = item.find('td', {'id': 'srp_tuple_primary_area'}).text
                apartment['Price'] = item.find('td', {'id': 'srp_tuple_price'}).text
                
            writer.writerow(apartment)
            print(apartment)
        
        time.sleep(5)
        page_count += 1
        print("Next Page")