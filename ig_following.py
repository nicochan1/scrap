from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import config
import time
from bs4 import BeautifulSoup
from ig_scrap import login, go_to_account_new
from ig_file import save_accounts_to_csv
from selenium.webdriver.chrome.options import Options 

chrome_options = Options()
chrome_options.add_argument('--headless=new')  # Modern headless mode
chrome_options.add_argument('--window-size=1920,1080')  # Set window size for headless mode
chrome_options.add_argument('--disable-gpu')  # Recommended for headless


    # Run this cell first
def run_following_script(driver,account):
    following_list = []

        
    # Then click the following link using JavaScript
    following_link = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, f"a[href='/{account}/following/']"))
    )

    driver.execute_script("arguments[0].click();", following_link)
    print('clicked following button')


    modal = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div[class='xyi19xy x1ccrb07 xtf3nb5 x1pc53ja x1lliihq x1iyjqo2 xs83m0k xz65tgg x1rife3k x1n2onr6']"))
    )
    print('modal found')
    scroll_count = 0

    #get and print the initial height
    initial_height = driver.execute_script("return arguments[0].scrollHeight", modal)
    print('Initial_height: ', initial_height)
    last_height = initial_height

    #scroll loop
    while True:
        #scroll to the bottom of the modal
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", modal)
        #wait 4 seconds
        time.sleep(4)
        print('Wait for 4 seconds')
        
        # get new scroll height
        new_height = driver.execute_script("return arguments[0].scrollHeight", modal)
        # if the new scroll height is greater than the last scroll height
        if new_height > last_height:
            #increment the scroll count
            scroll_count += 1
            print('Scrolled ', scroll_count)
            #print the new scroll height
            print('new_height: ', new_height)
            #update the last scroll height
            last_height = new_height
        # else break the loop because it's not scrolling anymore
        elif new_height == last_height:
            break

    #get the page source
    soup = BeautifulSoup(driver.page_source, "html.parser")

    #First find the dialog div
    dialog = soup.find('div', {'role': 'dialog'})

    #Then find all the links within the dialog
    accounts = dialog.find_all('a', 
        class_ = "x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz notranslate _a6hd"
        )

    unique_accounts = {account['href'].lstrip('/').split('/')[0] for account in accounts}  # Convert to set to remove duplicates


    #sort the accounts by name
    following_list.extend(sorted(unique_accounts, key=str.lower))

    return following_list


def get_following_list(account,driver):
    go_to_account_new(account,driver)
    list = run_following_script(driver,account)
    return list
    
if __name__ == '__main__':
    driver = webdriver.Chrome(options=chrome_options)
    print("opened the browser")
    driver.get("https://www.instagram.com")
    login(config.username2,config.password2,driver)
    print('wait 2 seconds')
    time.sleep(2)
    following_list = get_following_list("chang.10.25",driver)
    print("closed the browser")
    driver.quit()
    print('Number of following: ', len(following_list))
    print(following_list)
    save_accounts_to_csv(following_list)

