from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get("https://www.iplt20.com/players/virat-kohli/164")
time.sleep(3)

print("TITLE:", driver.title)
try:
    about_sections = driver.find_elements(By.CLASS_NAME, "player-details__bio")
    if about_sections:
        print("FOUND player-details__bio:", about_sections[0].text)
    else:
        # Just grab all paragraphs
        paragraphs = driver.find_elements(By.TAG_NAME, "p")
        for idx, p in enumerate(paragraphs):
            text = p.text.strip()
            if len(text) > 100:
                print(f"P {idx}:", text[:100], "...")
except Exception as e:
    print(e)
driver.quit()
