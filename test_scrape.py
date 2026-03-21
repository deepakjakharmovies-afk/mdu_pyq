from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os 
import pandas as pd
import time

options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

df_players = pd.read_csv("totals-teams-players.csv")

count = 0
for index, row in df_players.iterrows():
    if count >= 2:
        break
    
    url = row['Player Profile URL']
    if pd.isna(url) or not isinstance(url, str) or not url.startswith('http'):
        continue
    
    parts = url.rstrip('/').split('/')
    if len(parts) >= 2:
        player_name = parts[-2]
    else:
        continue

    print(f"Scraping {player_name} from {url}...")

    try:
        driver.get(url)

        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "sm-pp-table")))

        tables = driver.find_elements(By.CLASS_NAME, "sm-pp-table")
        
        if len(tables) < 2:
            print(f"Error: Could not find both batting and bowling tables for {player_name}.")
            continue

        def extract_table(table):
            rows = table.find_elements(By.TAG_NAME, "tr")
            if not rows: return pd.DataFrame()
            headers = [h.text for h in rows[0].find_elements(By.TAG_NAME, "th")]
            
            data = []
            for row in rows[1:]:
                cols = [c.text for c in row.find_elements(By.TAG_NAME, "td")]
                if cols:
                    data.append(cols)
            return pd.DataFrame(data, columns=headers)

        
        batting_df = extract_table(tables[0])
        bowling_df = extract_table(tables[1])

        os.makedirs(player_name, exist_ok=True)
        
        batting_df.to_json(f"{player_name}/batting_stats.json", orient="records", indent=4)
        bowling_df.to_json(f"{player_name}/bowling_stats.json", orient="records", indent=4)

        about_text = ""
        try:
            paragraphs = driver.find_elements(By.TAG_NAME, "p")
            for p in paragraphs:
                text = p.text.strip()
                if len(text) > 50:
                    about_text += text + "\n\n"
        except Exception as e:
            print(f"Could not extract about text for {player_name}: {e}")

        if about_text:
            with open(f"{player_name}/about.txt", "w", encoding="utf-8") as f:
                f.write(about_text.strip())

        print(f"Success! JSON and text files generated for {player_name}.")
        count += 1

    except Exception as e:
         print(f"Error scraping {player_name}: {e}")
         continue

driver.quit()
