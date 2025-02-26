from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import config
import time
import json
from bs4 import BeautifulSoup
from ig_file import get_last_scraped_photo, update_csv
import os
import requests
from urllib.parse import urlparse
import pandas as pd
from get_post_metadata import get_post_metadata
from datetime import datetime
from proxy_utils import random_delay, add_human_behavior, logger, is_rate_limited, handle_rate_limit_or_ban
import random

chrome_options = Options()

## headless mode
# chrome_options.add_argument('--headless=new')  # Modern headless mode
# chrome_options.add_argument('--window-size=1920,1080')  # Set window size for headless mode
# chrome_options.add_argument('--disable-gpu')  # Recommended for headless

#login function
def login(username_text,password_text,driver):    
    try:
        username = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='username']")))
        random_delay(0.5, 1.5)
        
        password = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='password']")))
        
        # Clear and type with random delays between keystrokes to mimic human typing
        username.clear()
        for char in username_text:
            username.send_keys(char)
            time.sleep(random.uniform(0.05, 0.2))
        
        random_delay(0.5, 1)
        
        password.clear()
        for char in password_text:
            password.send_keys(char)
            time.sleep(random.uniform(0.05, 0.2))
        
        random_delay(0.5, 1.5)
        
        button = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
        button.click()
        logger.info(f'Logged in with: {username_text}')
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        raise

def search(query,driver):
    try:
        search_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "svg[aria-label='Search']")))
        search_button.click()
        random_delay()
        
        search_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[placeholder='Search']"))
        )
        logger.info('Located search input')
        
        search_input.clear()
        random_delay(0.5, 1)
        
        # Type query with random delays between keystrokes
        for char in query:
            search_input.send_keys(char)
            time.sleep(random.uniform(0.05, 0.2))
            
        random_delay(1, 2)
    except Exception as e:
        logger.error(f"Search failed: {str(e)}")
        raise

        #enter keyword and search
def go_to_account(account,driver):
    try:
        search(account, driver)
        random_delay()
        
        # Check if there is the account in search
        account_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//span[contains(text(), '{account}')]"))
        )
        account_link.click()
        logger.info(f'Navigated to account: {account}')
        
        # Check for rate limiting
        if is_rate_limited(driver):
            logger.warning(f"Rate limit detected while accessing account {account}")
            new_driver = handle_rate_limit_or_ban(driver, driver.current_url)
            if new_driver:
                return new_driver
            else:
                raise Exception("Could not bypass rate limiting")
        
        # Add human-like behavior
        random_delay(2, 4)
        add_human_behavior(driver)
        
        return driver
    except Exception as e:
        logger.error(f"Failed to navigate to account {account}: {str(e)}")
        raise

def get_total_posts(driver):
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    # Find div that contains the text 'posts' at any level
    post_element = soup.find('span', class_='html-span xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x1hl2dhg x16tdsg8 x1vvkbs')
    if post_element:
        post_count = int(post_element.text.replace(',', ''))
    else:
        post_count = 0
        print("No post element found")

    return post_count
    
def save_post_urls(driver, account):
    logger.info(f"Starting to save post URLs for {account}")
    # list to store the soup objects
    all_soup = []
    all_urls = []
    all_dates = []
    
    # Get the total number of posts
    total_posts = get_total_posts(driver)
    logger.info(f"Total posts for {account}: {total_posts}")
    
    # Scroll down to load more posts with random delays and human-like behavior
    posts_loaded = 0
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while posts_loaded < total_posts:
        # Add human-like scrolling behavior
        scroll_amount = random.randint(300, 800)
        driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
        random_delay(0.5, 1.5)
        
        # Sometimes scroll back up a bit to mimic human behavior
        if random.random() < 0.3:  # 30% chance
            driver.execute_script(f"window.scrollBy(0, -{random.randint(50, 200)});")
            random_delay(0.3, 0.8)
        
        # Continue scrolling down
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        random_delay(1, 3)
        
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            # Try to click "Load more" button if it exists
            try:
                load_more = driver.find_element(By.XPATH, "//button[contains(text(), 'Load more')]")
                load_more.click()
                random_delay(2, 4)
            except:
                # If we can't load more posts, break the loop
                logger.info("No more posts to load")
                break
        
        last_height = new_height
        
        # Count loaded posts
        posts = driver.find_elements(By.XPATH, "//a[contains(@href, '/p/')]")
        posts_loaded = len(posts)
        logger.info(f"Loaded {posts_loaded} posts out of {total_posts}")
        
        # Add a longer pause occasionally to avoid detection
        if random.random() < 0.2:  # 20% chance
            logger.info("Taking a longer break to avoid detection")
            random_delay(5, 10)
    
    # Get all post links
    post_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/p/')]")
    unique_urls = set()
    
    for link in post_links:
        post_url = link.get_attribute('href')
        if post_url and post_url not in unique_urls:
            unique_urls.add(post_url)
            
            # Extract shortcode from URL
            parsed_url = urlparse(post_url)
            path_parts = parsed_url.path.strip('/').split('/')
            shortcode = path_parts[-1] if path_parts else None
            
            if shortcode:
                # Get post metadata to extract date
                try:
                    metadata = get_post_metadata(post_url)
                    if metadata and "timestamp" in metadata:
                        # Convert timestamp to datetime object
                        date_obj = datetime.strptime(metadata["timestamp"], '%Y-%m-%d %H:%M:%S')
                        
                        all_urls.append(post_url)
                        all_dates.append(date_obj)
                        logger.info(f"Added post: {shortcode} from {date_obj}")
                        
                        # Add random delay between metadata requests
                        random_delay(1, 3)
                except Exception as e:
                    logger.error(f"Error getting metadata for {shortcode}: {str(e)}")
    
    # Sort posts by date (newest first)
    sorted_posts = sorted(zip(all_urls, all_dates), key=lambda x: x[1], reverse=True)
    
    if sorted_posts:
        all_urls, all_dates = zip(*sorted_posts)
    else:
        all_urls, all_dates = [], []
    
    logger.info(f"Found {len(all_urls)} unique posts for {account}")
    return all_urls, all_dates


def get_shortcode(urls):   
    shortcodes = []
    for url in urls:
        shortcode = url.split('/')[-2]
        print('shortcode: ', shortcode)
        shortcodes.append(shortcode)
    return shortcodes

def download_files(all_urls, all_dates, account):
    #check the last scraped date
    last_scraped_date = get_last_scraped_photo(account)
    print('last scraped date: ', last_scraped_date)
    
    # Create directory for account if it doesn't exist
    account_dir = os.path.join(config.base_dir, account)
    if not os.path.exists(account_dir):
        os.makedirs(account_dir)
    
    # Count metrics
    total_posts = len(all_urls)
    new_posts = 0
    downloaded_posts = 0
    
    for i, (url, date) in enumerate(zip(all_urls, all_dates)):
        try:
            # Check if we've already scraped this post
            if last_scraped_date and date <= last_scraped_date:
                print(f"Skipping post {i+1}/{total_posts} (already scraped)")
                continue
            
            new_posts += 1
            
            # Extract shortcode from URL
            parsed_url = urlparse(url)
            path_parts = parsed_url.path.strip('/').split('/')
            shortcode = path_parts[-1] if path_parts else None
            
            if not shortcode:
                logger.warning(f"Could not extract shortcode from URL: {url}")
                continue
            
            # Create filename
            filename = f"{date.strftime('%Y%m%d')}_{shortcode}.json"
            filepath = os.path.join(account_dir, filename)
            
            # Skip if file already exists
            if os.path.exists(filepath):
                print(f"Skipping post {i+1}/{total_posts} (file already exists)")
                continue
            
            # Get post metadata
            logger.info(f"Downloading post {i+1}/{total_posts}: {shortcode}")
            metadata = get_post_metadata(url)
            
            if metadata:
                # Save metadata to file
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, ensure_ascii=False, indent=4)
                
                downloaded_posts += 1
                logger.info(f"Saved metadata for post {shortcode}")
            else:
                logger.warning(f"Failed to get metadata for post {shortcode}")
            
            # Add random delay between requests to avoid rate limiting
            random_delay(2, 5)
            
            # Occasionally take a longer break
            if i > 0 and i % 5 == 0:  # Every 5 posts
                logger.info("Taking a longer break to avoid rate limiting")
                random_delay(8, 15)
                
        except Exception as e:
            logger.error(f"Error downloading post {url}: {str(e)}")
    
    # Update CSV with metrics
    update_csv(account, total_posts, new_posts, downloaded_posts)
    logger.info(f"Account {account}: Total posts: {total_posts}, New posts: {new_posts}, Downloaded: {downloaded_posts}")

def go_to_account_new(account,driver):
        search(account,driver)
        go_to_account(account,driver)
        print('Account: ', account)
        print('Total posts: ', get_total_posts(driver))


        

def run_scrap_script(account, driver):
    try:
        logger.info(f"Starting scraping for account: {account}")
        
        # Go to account page and check for rate limiting
        driver = go_to_account(account, driver)
        random_delay()
        
        # Get post URLs and dates
        all_urls, all_dates = save_post_urls(driver, account)
        
        if all_urls and all_dates:
            # Download files with random delays between requests
            download_files(all_urls, all_dates, account)
            logger.info(f"Completed scraping for account: {account}")
        else:
            logger.warning(f"No posts found for account: {account}")
            # Update CSV with zero metrics
            update_csv(account, 0, 0, 0)
    except Exception as e:
        logger.error(f"Error scraping account {account}: {str(e)}")
        # Continue with next account instead of crashing
        return



    
if __name__ == "__main__":
    driver = webdriver.Chrome(options=chrome_options)
    print("opened the browser")
    driver.get("https://www.instagram.com")
    login(config.username2,config.password2,driver)
    print('wait 2 seconds')
    time.sleep(2)
    run_scrap_script("tobylwx",driver)
    print("closed the browser")
    driver.quit()
