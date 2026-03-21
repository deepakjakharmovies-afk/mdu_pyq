from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--window-size=1920,1080")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")

print("Starting driver...")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

url = "https://www.iplt20.com/players/virat-kohli/164"
print(f"Fetching {url}")
driver.get(url)

try:
    print("Waiting for table...")
    wait = WebDriverWait(driver, 15)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "sm-pp-table")))
    
    tables = driver.find_elements(By.CLASS_NAME, "sm-pp-table")
    print(f"Found {len(tables)} tables.")
    
    about = ""
    for p in driver.find_elements(By.TAG_NAME, "p"):
        if len(p.text) > 50:
            print("ABOUT:", p.text[:100], "...")
            break
            
except Exception as e:
    print(f"Error: {e}")
    print("Saving page source to debug.html")
    with open("debug.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)

driver.quit()
