import random
import time
import config
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import logging
from selenium.common.exceptions import TimeoutException, WebDriverException

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def get_random_proxy():
    """Return a random proxy from the configured list"""
    if not config.use_proxies or not config.proxy_list:
        return None
    return random.choice(config.proxy_list)

def get_random_user_agent():
    """Return a random user agent from the configured list"""
    if not config.rotate_user_agents or not config.user_agents:
        return None
    return random.choice(config.user_agents)

def random_delay(min_delay=None, max_delay=None):
    """Sleep for a random amount of time between min_delay and max_delay"""
    min_delay = min_delay or config.min_delay
    max_delay = max_delay or config.max_delay
    delay = random.uniform(min_delay, max_delay)
    logger.info(f"Waiting for {delay:.2f} seconds")
    time.sleep(delay)

def setup_driver():
    """Set up and return a webdriver with proxy and user agent if configured"""
    chrome_options = Options()
    
    # Add proxy if enabled
    proxy = get_random_proxy()
    if proxy:
        logger.info(f"Using proxy: {proxy.split('@')[-1]}")  # Log only the IP part for privacy
        chrome_options.add_argument(f'--proxy-server={proxy}')
    
    # Add user agent if enabled
    user_agent = get_random_user_agent()
    if user_agent:
        logger.info(f"Using user agent: {user_agent}")
        chrome_options.add_argument(f'--user-agent={user_agent}')
    
    # Add additional options to make the browser more stealthy
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Create the driver
    driver = webdriver.Chrome(options=chrome_options)
    
    # Set page load timeout
    driver.set_page_load_timeout(config.page_load_timeout)
    
    # Execute CDP commands to prevent detection
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": user_agent})
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        })
        """
    })
    
    return driver

def rotate_proxy(driver):
    """Close the current driver and return a new one with a different proxy"""
    logger.info("Rotating proxy...")
    try:
        driver.quit()
    except:
        pass
    return setup_driver()

def add_human_behavior(driver):
    """Add random scrolls and mouse movements to mimic human behavior"""
    try:
        # Random scrolling
        scroll_amount = random.randint(300, 700)
        driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
        random_delay(0.5, 1.5)
        
        # Scroll back up a bit
        driver.execute_script(f"window.scrollBy(0, -{random.randint(100, 300)});")
        random_delay(0.5, 1.5)
    except Exception as e:
        logger.warning(f"Error while adding human behavior: {e}")

def handle_rate_limit_or_ban(driver, url, max_retries=3):
    """
    Handle rate limiting or IP bans by rotating proxies and retrying
    
    Args:
        driver: The current webdriver instance
        url: The URL that was being accessed when the ban occurred
        max_retries: Maximum number of retry attempts
        
    Returns:
        A new driver instance if successful, None if all retries failed
    """
    for attempt in range(max_retries):
        logger.warning(f"Detected possible rate limit or IP ban. Rotating proxy (attempt {attempt+1}/{max_retries})")
        
        # Rotate to a new proxy
        driver = rotate_proxy(driver)
        
        # Add a longer delay before retry
        random_delay(10, 20)
        
        # Try to access the URL again
        try:
            driver.get(url)
            
            # Check if we're still blocked
            if "challenge" in driver.current_url or "login" in driver.current_url:
                logger.warning("Still facing access issues after proxy rotation")
                continue
            
            # If we get here, we've successfully bypassed the block
            logger.info("Successfully bypassed access restriction with new proxy")
            return driver
            
        except (TimeoutException, WebDriverException) as e:
            logger.error(f"Error with new proxy: {str(e)}")
            continue
    
    # If we get here, all retries failed
    logger.error("All proxy rotation attempts failed. Consider taking a longer break.")
    return None

def is_rate_limited(driver):
    """
    Check if the current page indicates a rate limit or IP ban
    
    Args:
        driver: The current webdriver instance
        
    Returns:
        True if rate limited or banned, False otherwise
    """
    # Check URL for challenge or login redirect
    if "challenge" in driver.current_url or "login" in driver.current_url:
        return True
    
    # Check for common rate limit indicators in page source
    rate_limit_indicators = [
        "Please wait a few minutes before you try again",
        "Try Again Later",
        "temporarily blocked",
        "unusual activity",
        "suspicious activity"
    ]
    
    for indicator in rate_limit_indicators:
        if indicator in driver.page_source:
            return True
    
    return False 