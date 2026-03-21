from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os 
import pandas as pd

options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--window-size=1920,1080")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")

print("Initializing Chrome Driver...")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

print("Reading totals-teams-players.csv...")
try:
    df_players = pd.read_csv("totals-teams-players.csv")
except Exception as e:
    print(f"Error reading CSV: {e}")
    driver.quit()
    exit()

total_players = len(df_players)
print(f"Found {total_players} players to process.")

for index, row in df_players.iterrows():
    url = row['Player Profile URL']
    if pd.isna(url) or not isinstance(url, str) or not url.startswith('http'):
        print(f"[{index+1}/{total_players}] Skipping invalid URL for {row.get('Player Name', 'Unknown')}.")
        continue
    
    parts = url.rstrip('/').split('/')
    if len(parts) >= 2:
        player_name = parts[-2]
    else:
        print(f"[{index+1}/{total_players}] Skipping invalid URL structure: {url}")
        continue

    print(f"[{index+1}/{total_players}] Scraping {player_name} from {url}...")

    try:
        driver.get(url)

        # Wait for either table or just a short time before skipping
        wait = WebDriverWait(driver, 10)
        try:
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "sm-pp-table")))
        except:
            print(f"  Warning: Timeout waiting for tables on {player_name}'s page. Continuing.")
            continue

        tables = driver.find_elements(By.CLASS_NAME, "sm-pp-table")
        
        if len(tables) < 2:
            print(f"  Error: Only found {len(tables)} tables for {player_name}. Need at least 2 (batting and bowling).")
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
        
        batting_df.to_json(os.path.join(player_name, "batting_stats.json"), orient="records", indent=4)
        bowling_df.to_json(os.path.join(player_name, "bowling_stats.json"), orient="records", indent=4)

        about_text = ""
        try:
            paragraphs = driver.find_elements(By.TAG_NAME, "p")
            for p in paragraphs:
                text = p.text.strip()
                if len(text) > 50:
                    about_text += text + "\n\n"
        except Exception as e:
            print(f"  Could not extract about text for {player_name}: {e}")

        if about_text:
            with open(os.path.join(player_name, "about.txt"), "w", encoding="utf-8") as f:
                f.write(about_text.strip())
            print(f"  Success! Saved batting, bowling stats, and about text for {player_name}.")
        else:
            print(f"  Success! Saved batting and bowling stats for {player_name} (No about text found).")

    except Exception as e:
         print(f"  Error processing {player_name}: {e}")
         continue

driver.quit()
print("Scraping completed!")