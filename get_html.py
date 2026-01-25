import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

import os 


def fetch_page_source(url):
    chrome_options = uc.ChromeOptions()
    #chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-infobars")

    driver = None  # Initialize driver to None
    try:
        # Create the undetected-chromedriver instance
        driver = uc.Chrome(options=chrome_options)
        driver.get(url)
        print(f"Navigated to {url}")
        # Add an explicit wait for page content to load
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        html_content = driver.page_source
        soap = BeautifulSoup(html_content, 'lxml')
        with open(f"page_source{intyear}.html", "w", encoding="utf-8") as file:
            file.write(soap.prettify())
        print("Successfully retrieved HTML content.")
        
        parse_html(html_content)
        print("Data extraction completed and saved to season_details.txt.")

    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        if driver: # Ensure driver exists before trying to quit
            driver.quit()
def parse_html(html_content):
    
    soap = BeautifulSoup(html_content, 'lxml')
    Lists = soap.find_all("li",class_="ng-scope")
    for List in Lists:
        Match_name= List.find("span",class_="vn-matchOrder ng-binding ng-scope").text
        Stadium_location = List.find("p",class_="ng-binding").text.split(",")[-1]
        Stadium_Name = List.find("span",class_="ng-binding ng-scope").text
        Winner_team = List.find("div",class_="vn-ticketTitle ng-binding ng-scope").text
        Team_name=[]
        for i ,name in enumerate(List.find_all("h3",class_="ng-binding ng-scope")):
            if i == 1 or i == 3 :
                Team_name.append(name.text.strip())

        with open(f"season_details.txt", "a", encoding="utf-8") as file:
            file.write(f"The match name is {Match_name}\n")
            file.write(f"The match was played between {Team_name[0]} and {Team_name[1]}\n ")
            file.write(f"The match was played at {Stadium_Name.strip()} , {Stadium_location.strip()}\n")
            file.write(f"The winner of the match is {Winner_team.strip()}\n")
            file.write("---------------------------------------------------\n")
            file.write("---------------------------------------------------\n")
            file.write("---------------------------------------------------\n")


    
if __name__ == "__main__":
    print("Welcome to the IPL Match Scraper!")
    year = input("Enter the year: ")
    if year == '':
        intyear = 2025
    else:
        intyear = int(year)
    if intyear < 2008 or intyear > 2025:
        print("Please enter a valid year between 2008 and 2024.")
        exit(1)
    
    else:
        url = f"https://www.iplt20.com/matches/{year}"  
    
    print(url)
    page_source = fetch_page_source(url)
    