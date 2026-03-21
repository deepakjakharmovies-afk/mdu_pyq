import requests
import re
import csv

def save_all_ids():
    # Use the 2026 stats feed
    url = "https://ipl-stats-sports-mechanic.s3.ap-south-1.amazonaws.com/ipl/feeds/stats/700-allplayerstats.js"
    response = requests.get(url)
    
    # Extracting names and IDs using regex from the JS file
    # Pattern looks for "player_id":"123","player_name":"Name"
    matches = re.findall(r'"player_id":"(\d+)".*?"player_name":"(.*?)"', response.text)
    
    with open('ipl_2026_ids.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Player Name"])
        for pid, name in sorted(set(matches), key=lambda x: x[1]):
            writer.writerow([pid, name])
    
    print(f"Done! Created ipl_2026_ids.csv with {len(set(matches))} players.")

save_all_ids()