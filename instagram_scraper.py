import requests
from bs4 import BeautifulSoup
import json
import time
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import config
import csv
from urllib.parse import urlparse

def download_profile_posts(username):
    try:
        # Create directory if it doesn't exist
        if not os.path.exists(f"images/{username}"):
            os.makedirs(f"images/{username}")
            
        # Get the profile page
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        url = f'https://www.instagram.com/{username}/'
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Find the shared data script that contains post information
            scripts = soup.find_all('script')
            for script in scripts:
                if 'window._sharedData' in str(script):
                    json_data = str(script).split('window._sharedData = ')[1][:-10]
                    data = json.loads(json_data)
                    
                    # Extract image URLs from the data
                    if 'entry_data' in data and 'ProfilePage' in data['entry_data']:
                        posts = data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['edges']
                        
                        for post in posts:
                            if not post['node']['is_video']:
                                img_url = post['node']['display_url']
                                img_response = requests.get(img_url, headers=headers)
                                
                                if img_response.status_code == 200:
                                    filename = f"images/{username}/{post['node']['id']}.jpg"
                                    with open(filename, 'wb') as f:
                                        f.write(img_response.content)
                                    print(f"Downloaded: {filename}")
                                    time.sleep(2)  # Add delay between downloads
                    
    except Exception as e:
        print(f"Error downloading from {username}: {str(e)}")

def get_next_account_to_scrape():
    csv_file = os.path.join('scraped_data', 'instagram_accounts.csv')
    accounts_to_scrape = []
    
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if int(row['last_scrapped']) == 0:  # Only get accounts not yet scrapped
                accounts_to_scrape.append(row['account'])
    
    if accounts_to_scrape:
        return accounts_to_scrape[0]  # Return the first unscraped account
    return None

def mark_account_as_scraped(account, num_images, num_videos):
    csv_file = os.path.join('scraped_data', 'instagram_accounts.csv')
    rows = []
    
    # Read existing data
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['account'] == account:
                row['last_scrapped'] = int(time.time())  # Current timestamp
                row['num_images'] = num_images
                row['num_videos'] = num_videos
            rows.append(row)
    
    # Write updated data
    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['account', 'last_scrapped', 'num_images', 'num_videos'])
        writer.writeheader()
        writer.writerows(rows)

def login(driver, username, password):
    driver.get("https://www.instagram.com")
    
    username_field = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='username']")))
    password_field = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='password']")))
    
    username_field.clear()
    username_field.send_keys(username)
    password_field.clear()
    password_field.send_keys(password)
    
    button = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
    button.click()

def scrape_account(account):
    driver = webdriver.Chrome()
    try:
        # Login
        login(driver, config.username, config.password)
        time.sleep(3)  # Wait for login
        
        # Rest of your scraping code here...
        # (Copy the relevant parts from your notebook)
        
    finally:
        driver.quit()

if __name__ == '__main__':
    # This code only runs if the script is run directly
    account = get_next_account_to_scrape()
    if account:
        print(f"Scraping account: {account}")
        scrape_account(account)
    else:
        print("No accounts left to scrape!") 