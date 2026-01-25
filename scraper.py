import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import time
import os
from urllib.parse import urljoin

BASE_URL = "https://www.mdustudy.com/mdu-btech-question-papers.html"
PAPERS_BASE_URL = "https://www.mdustudy.com/"
PDF_DIR = "pdfs"

def parse_paper_text(text, html_url):
  
    data = {
        "text": text,
        "branch": "COMMON/N/A",
        "semester": "N/A",
        "subject": "N/A",
        "subject_code": "N/A",
        "month": "N/A",
        "year": "N/A",
        "html_url": html_url,
        "pdf_url": html_url.replace('.html', '.pdf')
    }

    # Extract Year (usually 4 digits at the end)
    year_match = re.search(r'(\d{4})$', text)
    if year_match:
        data["year"] = year_match.group(1)
        text = text[:year_match.start()].strip('-')

    # Extract Month (usually before year)
    month_match = re.search(r'(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)$', text, re.IGNORECASE)
    if month_match:
        data["month"] = month_match.group(1).upper()
        text = text[:month_match.start()].strip('-')

    # Extract Semester
    sem_match = re.search(r'(\d+)-SEM', text, re.IGNORECASE)
    if sem_match:
        data["semester"] = sem_match.group(1)
        text = re.sub(r'\d+-SEM-?', '', text, flags=re.IGNORECASE).strip('-')

    # Extract Branch
    if text.startswith("BTECH-"):
        text = text[len("BTECH-"):].strip('-')
        branches = ["CSE", "CIVIL", "ME", "ECE", "IT", "CHEMICAL", "TT", "FT", "BIO", "AEIE", "AUE", "BT", "EE", "EEE"]
        for b in branches:
            if text.startswith(b):
                data["branch"] = b
                text = text[len(b):].strip('-')
                break

    # Extract Subject Code
    code_match = re.search(r'-(\d{4,5})$', text)
    if code_match:
        data["subject_code"] = code_match.group(1)
        text = text[:code_match.start()].strip('-')

    # Remaining text is the subject
    data["subject"] = text.replace('-', ' ')

    return data

def get_links_from_url(url):
    print(f"Fetching links from: {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.get_text(strip=True)
            if '/papers/' in href and href.endswith('.html'):
                full_url = urljoin(PAPERS_BASE_URL, href)
                links.append((text, full_url))
        return links
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []

def download_pdf(pdf_url, filename):
    filepath = os.path.join(PDF_DIR, filename)
    if os.path.exists(filepath):
        return True # Already downloaded
    
    try:
        response = requests.get(pdf_url, stream=True)
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
        else:
            print(f"Failed to download {pdf_url}: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"Error downloading {pdf_url}: {e}")
        return False

def main():
    if not os.path.exists(PDF_DIR):
        os.makedirs(PDF_DIR)

    branch_urls = [
        "https://www.mdustudy.com/mdu-btech-question-papers.html",
        "https://www.mdustudy.com/btech-cse-question-papers.html",
        "https://www.mdustudy.com/btech-civil-question-papers.html",
        "https://www.mdustudy.com/btech-me-question-papers.html",
        "https://www.mdustudy.com/btech-e-all-question-papers.html",
        "https://www.mdustudy.com/btech-it-question-papers.html",
        "https://www.mdustudy.com/btech-chemical-question-papers.html",
        "https://www.mdustudy.com/btech-tt-question-papers.html",
        "https://www.mdustudy.com/btech-ft-question-papers.html",
        "https://www.mdustudy.com/btech-bio-question-papers.html",
        "https://www.mdustudy.com/btech-aeie-question-papers.html",
        "https://www.mdustudy.com/btech-aue-question-papers.html",
        "https://www.mdustudy.com/btech-others-question-papers.html"
    ]

    all_papers = []
    seen_urls = set()

    print("--- Scraping Paper Links ---")
    for url in branch_urls:
        links = get_links_from_url(url)
        for text, link in links:
            if link not in seen_urls:
                seen_urls.add(link)
                metadata = parse_paper_text(text, link)
                all_papers.append(metadata)
        time.sleep(1)

    if not all_papers:
        print("No papers found.")
        return

    df = pd.DataFrame(all_papers)
    df['year_sort'] = pd.to_numeric(df['year'], errors='coerce').fillna(0).astype(int)
    df = df.sort_values(by=['year_sort', 'subject', 'branch'], ascending=[False, True, True])
    df = df.drop(columns=['year_sort'])

    output_file = "mdu_btech_pyqs.csv"
    df.to_csv(output_file, index=False)
    print(f"Saved {len(df)} paper records to {output_file}")

    # Download ALL papers
    print(f"\n--- Downloading All PDFs ({len(df)} papers) ---")
    print("This may take some time. Please be patient...")
    for i, row in df.iterrows():
        filename = row['pdf_url'].split('/')[-1]
        # Skip if filename is empty or invalid
        if not filename or not filename.endswith('.pdf'):
            continue
            
        print(f"[{i+1}/{len(df)}] Downloading: {filename}")
        if download_pdf(row['pdf_url'], filename):
            # Success (or already exists)
            pass
        else:
            print(f"Failed to download {filename}")
        
        # Adding a small delay to be polite to the server
        # and avoid getting blocked
        time.sleep(0.5)

    print(f"\nScraping and downloading complete. Results saved to {output_file} and files in '{PDF_DIR}' folder.")

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
