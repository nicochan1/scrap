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

chrome_options = Options()
chrome_options.add_argument('--headless=new')  # Modern headless mode
chrome_options.add_argument('--window-size=1920,1080')  # Set window size for headless mode
chrome_options.add_argument('--disable-gpu')  # Recommended for headless

#login function
def login(username_text,password_text,driver):    
    username = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='username']")))
    password = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='password']")))
    
    username.clear()
    username.send_keys(username_text)
    password.clear()
    password.send_keys(password_text)
    
    button = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
    button.click()
    print('login with: ', username_text)

def search(query,driver):
    search_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "svg[aria-label='Search']")))
    search_button.click()
    
    search_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "input[placeholder='Search']"))
    )
    print('located search input')
    
    search_input.clear()
    search_input.send_keys(query)
    search_input.send_keys(Keys.RETURN)
    print('search account: ', query)

        #enter keyword and search
def go_to_account(account,driver):
    #Check if there is the account in search
    try:
        # Find the span with exact text content and click its parent link
        clickable_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//span[text()='{account}']/ancestor::a"))
        )
        driver.execute_script("arguments[0].click();", clickable_element)
        print('go to account: ', account)
    except TimeoutException:
        print(f"Could not click on result for '{account}'")
    time.sleep(2)

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
    #list to store the soup objects
    soups = []
    #list to store the post image urls
    post_urls = []

    max_scroll_count = 50

    #Get the initial page height
    initial_height = driver.execute_script("return document.body.scrollHeight")
    print("Initial height: ", initial_height)

    i = 0
    while i < max_scroll_count:
        #Parse the HTML
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        elements = soup.find_all('a', href=lambda x: (f"/{account}/p/" in x or f"/{account}/reel/" in x) if x else False)
        print("Post Scraped: ", len(elements), '/', get_total_posts(driver))
        soups.append(soup)

        #scroll to the bottom of the page
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        i += 1

        #Get the current page height
        current_height = driver.execute_script("return document.body.scrollHeight")
        print("Scroll ", i, ' Current height: ', current_height)

        #wait for the page to load
        time.sleep(2)
        print("Waiting 2 seconds for page to load")

        #if there is no more scrollable content
        if current_height == initial_height:

            #try to scroll again
            current_height = driver.execute_script("return document.body.scrollHeight")
            time.sleep(3)
            print("Waiting 3 more seconds for page to load")
            if current_height > initial_height:
                i+=1
                print("Scroll ", i, ' Current height: ', current_height)

            #if there is no more scrollable content
            elif current_height == initial_height:
                #try to scroll again
                current_height = driver.execute_script("return document.body.scrollHeight")
                time.sleep(4)
                print("Waiting 4 more seconds for page to load")
                if current_height > initial_height:
                    i+=1
                    print("Scroll ", i, ' Current height: ', current_height)

                #if there is no more scrollable content
                elif current_height == initial_height:
                    #to the end already
                    print("No more scrollable content")
                    break   #exit the loop when you can't scroll further

        # Update the initial height for the next iteration
        initial_height = current_height

        # loop through soup elements
    for soup in soups:

        # Find elements by href pattern including p or reel
        elements = soup.find_all('a', href=lambda x: (f"/{account}/p/" in x or f"/{account}/reel/" in x) if x else False)
            

        #Extract the href attributes and filter URLs that start with "/p/" or "/reel/"
        post_urls.extend([element['href'] for element in elements if '/p/' in element['href'] or '/reel/' in element['href']])

    #conver the list to a set to remove duplicates
    unique_post_urls = list(set(post_urls))

    print("Number of post scraped: ",len(unique_post_urls), '/', get_total_posts(driver)
          , ' ', int((len(unique_post_urls)/get_total_posts(driver) * 100)), '%')    

    return unique_post_urls

def get_json_data(driver, unique_post_urls):
#Create a list to store the json for each post
    print("getting post JSON data")
    json_list =[]

    # Define the query parameters to add
    query_params = "__a=1&__d=dis"
    No_of_photo_url = 0
    i=0
    #go through all urls
    for url in unique_post_urls:
        i+=1
        #Error handling
        try:
            #skip if the url is reel
            if '/reel/' in url:
                print(i, '/',len(unique_post_urls), ' skip reel ', url)
                continue
            
            #Append the query parameters to the URL
            modified_url = "https://www.instagram.com" + url + "?" + query_params

            #get URL
            driver.get(modified_url)
            print(i, '/',len(unique_post_urls), ' ', modified_url)
            No_of_photo_url += 1

            #Find the <pre> tag containing the JSON data
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//pre"))
            )
            pre_tag = driver.find_element(By.XPATH, '//pre')  # Updated this line

            #Extract the JSON data from the <pre> tag
            json_script = pre_tag.text
            
            #Parse the JSON data
            json_parsed = json.loads(json_script)

            #Add json to the list
            json_list.append(json_parsed)

        except (NoSuchElementException, TimeoutException, json.JS) as e:
            print(f"Error processing URL {url}: {e}")

    print("Get post JSON data completed")
    return json_list

def scrape_data(json_list):
    all_urls = []
    all_dates = []

    #iterate through each JSON data in the list
    for json_data in json_list:

        #Extract the list from the 'items' key
        item_list = json_data.get('items',[])

        #iterate through each item in 'items' list
        for item in item_list:

            #extract the date the item was taken
            date_taken = item.get('taken_at')

            #check if the carousel media is present
            carousel_media = item.get('carousel_media',[])

            #iterate through each item in the 'carousel_media' list
            for media in carousel_media:

                #extract the image url from the media
                image_url = media.get('image_versions2', {}).get('candidates', [])[0].get('url')

                #check if the image_url field is found inside the 'carousel_media' list
                if image_url:

                    #Add the image url and corresponding date to the lists
                    all_urls.append(image_url)
                    all_dates.append(date_taken)
                    print("carousel image scraped")

                #Extract the video URL from the media
                video_versions = media.get('video_versions', [])
                if video_versions:
                    video_url = video_versions[0].get('url')
                    if video_url:
                        #Add the video URL and corresponding date to the lists
                        all_urls.append(video_url)
                        all_dates.append(date_taken)
                        print("carousel video scraped")
            
            #handle cases of unique image, instead of carousel
            image_url = item.get('image_versions2', {}).get('candidates', [])[0].get('url')
            if image_url:
                #Add the image URL and corresponding date to the lists
                all_urls.append(image_url)
                all_dates.append(date_taken)
                print("single image scraped")

            #check if 'video_versions' key exists
            video_versions =  item.get('video_versions', [])
            if video_versions:
                video_url = video_versions[0].get('url')
                if video_url:
                    #Add the video URL and corresponding date to the lists
                    all_urls.append(video_url)
                    all_dates.append(date_taken)
                    print("single video scraped")

    print("Total number of photos/videos scraped: ", len(all_urls))

    return all_urls, all_dates


def download_files(all_urls, all_dates, account):
    #check the last scraped date
    last_scraped_photo = get_last_scraped_photo(account)
    print('Last scraped photo: ', last_scraped_photo)
    
    #Create the base directory for alll scapped data
    os.makedirs(config.base_dir, exist_ok=True)
    download_dir = os.path.join(config.base_dir, account)

    #Create subfolders for images and videos
    image_dir = os.path.join(download_dir, "images")
    video_dir = os.path.join(download_dir, "videos")
    os.makedirs(image_dir, exist_ok=True)
    os.makedirs(video_dir, exist_ok=True)

    image_counter = 1
    video_counter = 1
    image_added = 0
    video_added = 0
    this_time_scraped_photo = 0
  

    #iterate through URLs in the all_urls list and download media
    for index, url in enumerate(all_urls, 0):

        #check if the date is older than the last scraped date, skip if true
        if all_dates[index] <= last_scraped_photo:
            print(f'{index+1}/{len(all_urls)} Skipping {all_dates[index]} because it is older than the last scraped photo')
            continue
        response =  requests.get(url, stream=True)


        #Extract file extension from the URL
        url_path =  urlparse(url).path
        file_extension = os.path.splitext(url_path)[1]


        #Determine the file name based on the URL
        if file_extension.lower() in {'.jpg', '.jpeg', '.png', '.gof', '.heic', '.webp'}:
            if index > 0 and all_dates[index] == all_dates[index-1]:
                image_counter += 1
            else:
                image_counter = 1
            file_name = f"{all_dates[index]}-img-{image_counter}.png"
            destination_folder = image_dir
            image_added += 1

        elif file_extension.lower() in {'.mp4', '.avi', '.mkv', '.mov'}:
            if index > 0 and all_dates[index] == all_dates[index-1]:
                video_counter += 1
            else:
                video_counter = 1
            file_name = f"{all_dates[index]}-img-{video_counter}.mp4"
            destination_folder = video_dir
            video_added += 1
        else:
            #Default to the main download directory for other file types
            file_name = f"{all_dates[index]}{file_extension}"
            destination_folder = download_dir

        #Save the file to the appropriate folder
        file_path = os.path.join(destination_folder, file_name)

        #Write the content of the response to the file
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)

        print(f'{index+1}/{len(all_urls)} Downloaded: {all_dates[index]}, Last scraped photo: {last_scraped_photo}')
        if all_dates[index] > this_time_scraped_photo:
            this_time_scraped_photo = all_dates[index]
            print('lastest scraped photo: ', this_time_scraped_photo)

    #Print a message indicating the number of downloaded files and the download directory
    print(f'Image files downloaded: {image_added}')
    print(f'Video files downloaded: {video_added}')
    update_csv(account, this_time_scraped_photo, image_added, video_added)
 

def go_to_account_new(account,driver):
        search(account,driver)
        go_to_account(account,driver)
        print('Account: ', account)
        print('Total posts: ', get_total_posts(driver))

def run_scrap_script(account,driver):
    if account != []:
        go_to_account_new(account,driver)
        total_posts = get_total_posts(driver)
        if total_posts > 0:
            unique_post_urls = save_post_urls(driver, account)
            json_list = get_json_data(driver, unique_post_urls)
            all_urls, all_dates = scrape_data(json_list)
            download_files(all_urls, all_dates, account)
        else:
            #if no posts found, just update the reference date
            update_csv(account, 0, 0, 0)
            print('No posts found for account: ', account)



    
if __name__ == "__main__":
    driver = webdriver.Chrome(options=chrome_options)
    print("opened the browser")
    driver.get("https://www.instagram.com")
    login(config.username2,config.password2,driver)
    print('wait 2 seconds')
    time.sleep(2)
    run_scrap_script("kwanlam218",driver)
    print("closed the browser")
    driver.quit()

