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
options.add_argument("--headless=new")
options.add_argument("--window-size=1920,1080")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")

print("Initializing Chrome Driver...")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def extract_table(table):
    try:
        rows = table.find_elements(By.TAG_NAME, "tr")
        if not rows: return pd.DataFrame()
        headers = [h.text.strip() for h in rows[0].find_elements(By.TAG_NAME, "th")]
        
        data = []
        for row in rows[1:]:
            cols = [c.text.strip() for c in row.find_elements(By.TAG_NAME, "td")]
            if cols:
                data.append(cols)
        return pd.DataFrame(data, columns=headers)
    except:
        return pd.DataFrame()

df_players = pd.read_csv("totals-teams-players.csv")
existing_dirs = [d for d in os.listdir('.') if os.path.isdir(d)]

missing_players = []
for index, row in df_players.iterrows():
    url = row['Player Profile URL']
    if pd.isna(url) or not isinstance(url, str) or not url.startswith('http'):
        continue
    name_slug = url.rstrip('/').split('/')[-2]
    if name_slug not in existing_dirs:
        missing_players.append((name_slug, url))

print(f"Total players in CSV: {len(df_players)}")
print(f"Already scraped: {len(existing_dirs)}")
print(f"Remaining to scrape: {len(missing_players)}")

for i, (player_name, url) in enumerate(missing_players):
    print(f"[{i+1}/{len(missing_players)}] Scraping {player_name} from {url}...")
    
    try:
        driver.get(url)
        time.sleep(2) # Minimal wait

        # Try to find all tables
        tables = driver.find_elements(By.CLASS_NAME, "sm-pp-table")
        
        os.makedirs(player_name, exist_ok=True)
        saved_anything = False

        if tables:
            # Look for context (Batting/Bowling) in the parent or previous elements
            for table in tables:
                try:
                    # Look for a heading nearby
                    parent = table.find_element(By.XPATH, "./..")
                    heading = ""
                    try:
                        heading = parent.find_element(By.TAG_NAME, "h3").text.lower()
                    except:
                        try:
                            heading = parent.find_element(By.XPATH, "./preceding-sibling::*[1]").text.lower()
                        except:
                            pass
                    
                    df = extract_table(table)
                    if not df.empty:
                        prefix = "table"
                        if "batting" in heading: prefix = "batting_stats"
                        elif "bowling" in heading: prefix = "bowling_stats"
                        else:
                            # Fallback check headers
                            cols = [c.lower() for c in df.columns]
                            if 'runs' in cols and 'avg' in cols: prefix = "batting_stats"
                            elif 'wickets' in cols or 'overs' in cols: prefix = "bowling_stats"
                        
                        df.to_json(os.path.join(player_name, f"{prefix}.json"), orient="records", indent=4)
                        saved_anything = True
                except:
                    continue

        # Always try to get About text
        about_text = ""
        try:
            paragraphs = driver.find_elements(By.TAG_NAME, "p")
            for p in paragraphs:
                text = p.text.strip()
                if len(text) > 40:
                    about_text += text + "\n\n"
        except:
            pass
        
        if about_text:
            with open(os.path.join(player_name, "about.txt"), "w", encoding="utf-8") as f:
                f.write(about_text.strip())
            saved_anything = True

        if saved_anything:
            print(f"  Success! Data saved for {player_name}.")
        else:
            print(f"  Warning: No significant data found for {player_name}.")

    except Exception as e:
        print(f"  Error scraping {player_name}: {e}")

driver.quit()
print("Process finished.")
