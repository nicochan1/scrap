from ig_file import read_accounts_from_csv
from ig_scrap import run_scrap_script, login
import config
import time
from proxy_utils import (
    setup_driver, random_delay, rotate_proxy, add_human_behavior, 
    logger, is_rate_limited, handle_rate_limit_or_ban
)

print('Program start')
logger.info("Starting Instagram scraper")

# Read and print account list
account_list = read_accounts_from_csv()
number_of_accounts = len(account_list)
print('Account list: ', account_list)
print('number of accounts: ', number_of_accounts)
logger.info(f"Found {number_of_accounts} accounts to scrape")

# Open browser with proxy and user agent rotation
driver = setup_driver()
logger.info("Browser opened with proxy configuration")

# Go to instagram and login
driver.get("https://www.instagram.com")
logger.info("Navigating to Instagram")
random_delay()  # Random delay before login

# Check for rate limiting
if is_rate_limited(driver):
    logger.warning("Rate limit detected during initial access")
    driver = handle_rate_limit_or_ban(driver, "https://www.instagram.com")
    if not driver:
        logger.error("Could not bypass rate limiting. Exiting.")
        print("Program terminated due to persistent rate limiting")
        exit(1)

login(config.username2, config.password2, driver)
logger.info(f"Logged in as {config.username2}")

# Wait with random delay
random_delay(3, 6)  # Longer delay after login

# Counter for proxy rotation
requests_count = 0
max_requests_per_proxy = 5  # Rotate proxy after this many requests

i = 0
for account in account_list:
    i += 1
    if i > 3:
        break
    
    logger.info(f"[{i}/{number_of_accounts}] Starting to scrape account: {account}")
    
    # Rotate proxy after certain number of requests
    requests_count += 1
    if requests_count >= max_requests_per_proxy and config.use_proxies:
        driver = rotate_proxy(driver)
        requests_count = 0
        
        # Need to login again after proxy rotation
        driver.get("https://www.instagram.com")
        
        # Check for rate limiting after proxy rotation
        if is_rate_limited(driver):
            driver = handle_rate_limit_or_ban(driver, "https://www.instagram.com")
            if not driver:
                logger.error("Could not bypass rate limiting. Skipping to next account.")
                continue
        
        random_delay()
        login(config.username2, config.password2, driver)
        random_delay(3, 6)
    elif i > 1:
        # Add some human-like behavior
        add_human_behavior(driver)
        
        driver.get("https://www.instagram.com")
        logger.info("Navigating back to Instagram homepage")
        
        # Check for rate limiting
        if is_rate_limited(driver):
            driver = handle_rate_limit_or_ban(driver, "https://www.instagram.com")
            if not driver:
                logger.error("Could not bypass rate limiting. Skipping to next account.")
                continue
        
        random_delay()

    # Run the scraping with random delays between actions
    try:
        run_scrap_script(account, driver)
        
        # Check if we got rate limited during scraping
        if is_rate_limited(driver):
            logger.warning(f"Rate limit detected after scraping {account}")
            driver = handle_rate_limit_or_ban(driver, driver.current_url)
            if not driver:
                logger.error("Could not bypass rate limiting. Taking a longer break.")
                time.sleep(300)  # 5 minute break
                driver = setup_driver()  # Create a fresh driver
    except Exception as e:
        logger.error(f"Error during scraping: {str(e)}")
        # If we encounter an error, try rotating the proxy
        driver = rotate_proxy(driver)
        requests_count = 0
    
    # Add longer delay between accounts
    random_delay(5, 10)

logger.info("Finished scraping all accounts")
driver.quit()
logger.info("Browser closed")
print('Program end')


