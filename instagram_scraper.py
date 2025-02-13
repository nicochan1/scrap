import requests
from bs4 import BeautifulSoup
import json
import time
import os

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

# List of Instagram accounts
accounts = [
    'barbielee1004'
]

# Process each account
for account in accounts:
    print(f"Downloading images from {account}")
    download_profile_posts(account)
    time.sleep(5)  # Add delay between accounts 