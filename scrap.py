from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
import requests
from bs4 import BeautifulSoup
import re
import json
import os
from urllib.parse import urlparse
import csv
import config  # Add this import at the top with other imports

#setup chrome options
driver = webdriver.Chrome()

#open the website
driver.get("https://www.instagram.com")


#find the username input field
username = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='username']")))
password = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='password']")))

print(username)
print(password)
#enter the username and password
username.clear()
username.send_keys(config.username)
password.clear()
password.send_keys(config.password)

#targer the login button and click it
button = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
button.click()

#wait for search button to be clickable
search_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "svg[aria-label='Search']")))
search_button.click()

#target the search input field
search_input = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, "input[placeholder='Search']"))
)

#enter the search query
search_input.clear()
search_input.send_keys("instagram")
search_input.send_keys(Keys.RETURN)

# Wait for login to complete and keep browser open
try:
    # Wait for home page to load (looking for a common element on Instagram home page)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "svg[aria-label='Home']"))
    )
    # Keep browser open
    input("Press Enter to close the browser...")
except Exception as e:
    print(f"Login failed: {e}")
finally:
    driver.quit()



