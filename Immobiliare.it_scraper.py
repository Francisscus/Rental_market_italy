import csv
from time import sleep, time
import numpy as np
from selenium.webdriver import Chrome
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


#this dictionary cannot be used because some css selectors change from city page to city page,
#therefore the process cannot be automatized from the initial phase which has to be performed manually
#I kept the dictionary with city and target url of 5 out of 20 cities I selected to give an idea of what I used
{'Napoli': 'https://www.immobiliare.it/affitto-case/napoli/?criterio=rilevanza',
 'Genova': 'https://www.immobiliare.it/affitto-case/genova/?criterio=rilevanza',
 'Torino': 'https://www.immobiliare.it/affitto-case/torino/?criterio=rilevanza',
 'Roma':   'https://www.immobiliare.it/affitto-case/roma/?criterio=rilevanza',
 'Milano': 'https://www.immobiliare.it/affitto-case/milano/?criterio=rilevanza'}

# when you change the city, control to modify also:
# - target_url
# - csv file name: number_rent_city.csv
# - the number put in the csv file title is used just to order the 20 files

target_url = 'https://www.immobiliare.it/affitto-case/milano/?criterio=rilevanza'

# this few lines allow you to install the driver only when you use the script instead of download and update it everytime
chrome_driver = ChromeDriverManager().install()
driver = Chrome(service=Service(chrome_driver))
driver.get(target_url)

start_time = time()
print(f'Start_time {start_time}')

# create a csv file to fill with scraped information
with open('19_rent_taranto.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

    # refuse cookies
    driver.find_element(By.CSS_SELECTOR, "span.didomi-continue-without-agreeing").click()
    sleep(2)
    # refuse the option to saved the research
    try:
        driver.find_element(By.CSS_SELECTOR, "button.nd-dialogFrame__close").click()
    except:
        pass

    # below, there is the information I collected from each rental ad
    header = ["Index", "Title description", "Price", "N_rooms", "Surface", "N_toilettes", "Floor"]
    writer.writerow(header)

    # the number of pages to scrape might vary from city to city,
    # therefore, it is necessary to change the index between square brackets to find the right css selector
    # remember that find_elements is plural because it takes identical css selectors and store them in a list
    last_page_number = int((driver.find_elements(By.CSS_SELECTOR, ".in-pagination__item.hideOnMobile")[3]).text)

    num = 0
    for num_page in range(1, last_page_number+1):
        print(f'Starting page: {num_page}')
        driver.implicitly_wait(3) #this wait allows to load a new page, otherwise we cannot scrape anything

        # the following line is necessary to find the box of the ad that contains all the elements of each rent in the web page
        houses = driver.find_elements(By.CSS_SELECTOR,
        ".in-card.nd-mediaObject.nd-mediaObject--colToRow.in-realEstateCard.in-realEstateCard--interactive.in-realEstateListCard")

        # for each box we find in the web page we can iterate and bring the information we want
        for house in houses:
            num += 1
            title = house.find_element(By.CSS_SELECTOR, "a.in-card__title")
            title = title.text

            try:
                price = house.find_element(By.CSS_SELECTOR, 'li.in-feat__item--main').text
                price = price.replace("€ ", "")
                price = price.replace(".", "")
                price = price.replace("/mese", "")
                if price == 'PREZZO SU RICHIESTA':
                    price = np.NaN
                else:
                    price = float(price[0:4])
            except NoSuchElementException: # the program raises this exception when the information we are looking for doesn't exist
                price = np.NaN

            try:
                rooms = house.find_element(By.CSS_SELECTOR, 'li[aria-label="locali"]').text
            except NoSuchElementException:
                rooms = np.NaN

            try:
                surface = house.find_element(By.CSS_SELECTOR, 'li[aria-label = "superficie"]').text
                surface = float(surface.replace("m²", ""))
            except NoSuchElementException:
                surface = np.NaN

            try:
                n_toilettes = house.find_element(By.CSS_SELECTOR, 'li[aria-label = "bagni"]').text
            except NoSuchElementException:
                n_toilettes = np.NaN

            try:
                floors = house.find_element(By.XPATH, '//li[@aria-label="piano"]').text
                if floors == 'T':
                    floors = 0
            except NoSuchElementException:
                floors = np.NaN

            print(num, title, price, rooms, surface, n_toilettes, floors)

            row = [int(num), title, price, rooms, surface, n_toilettes, floors]

            writer.writerow(row)

        execution_time = round((time() - start_time) / 60, 2)
        print(f'Execution time : {execution_time} minutes')

        #the following lines are used to find the next page and click on it until the last one
        if num_page == 1:
           WebDriverWait(driver, 1).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "a[class$='in-pagination__item']"))
                ).click()
        elif num_page > 1:
            sleep(1.5)
            new_page = driver.find_elements(By.CSS_SELECTOR, "a[class$='in-pagination__item']")[1]
            new_page.click()


driver.quit() # when we arrive to the last page, this line closes the program
