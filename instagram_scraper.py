import instaloader
import time

# Initialize Instaloader
L = instaloader.Instaloader()

# List of Instagram accounts
accounts = [
    'account1',
    'account2',
    'account3'
]

# Login (optional but recommended to avoid restrictions)
# L.login('your_username', 'your_password')

def download_profile_posts(username):
    try:
        # Get profile
        profile = instaloader.Profile.from_username(L.context, username)
        
        # Download posts
        for post in profile.get_posts():
            # Download only images (skip videos)
            if not post.is_video:
                L.download_post(post, target=f"images/{username}")
                time.sleep(2)  # Add delay to avoid being blocked
                
    except Exception as e:
        print(f"Error downloading from {username}: {str(e)}")

# Process each account
for account in accounts:
    print(f"Downloading images from {account}")
    download_profile_posts(account)
    time.sleep(5)  # Add delay between accounts 