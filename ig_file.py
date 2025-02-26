import os
import pandas as pd
import config
from datetime import datetime
import logging

# Set up logging
logger = logging.getLogger(__name__)

csv_file = os.path.join(config.base_dir, config.csv_file_name)
seperator = '\t'
        
def update_csv(account, total_posts, new_posts, downloaded_posts):
    # Create base directory if it doesn't exist
    os.makedirs(config.base_dir, exist_ok=True)
    
    # Create CSV file if it doesn't exist
    if not os.path.exists(csv_file):
        df = pd.DataFrame(columns=['account', 'last_scrapped', 'total_posts', 'new_posts', 'downloaded_posts', 'reference_date'])
        df.to_csv(csv_file, index=False, sep=seperator)
        logger.info(f"Created new CSV file: {csv_file}")
    
    # Read the CSV file
    df = pd.read_csv(csv_file, sep=seperator)
    
    # Get current timestamp
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # If account exists in the CSV
    if account in df['account'].values:
        # If new posts were downloaded
        if downloaded_posts > 0:
            # Update last_scrapped, metrics and reference_date
            df.loc[df['account'] == account, ['last_scrapped', 'total_posts', 'new_posts', 'downloaded_posts', 'reference_date']] = [
                current_time,
                total_posts,
                int(df.loc[df['account'] == account, 'new_posts'].iloc[0]) + new_posts,
                int(df.loc[df['account'] == account, 'downloaded_posts'].iloc[0]) + downloaded_posts,
                current_time
            ]
            logger.info(f"Updated CSV for {account}: {downloaded_posts} new posts downloaded")
        else:
            # Only update reference_date and total_posts if no new files downloaded
            df.loc[df['account'] == account, ['total_posts', 'reference_date']] = [
                total_posts,
                current_time
            ]
            logger.info(f"Updated CSV for {account}: No new posts downloaded")
    else:
        # Add new account to CSV
        new_row = pd.DataFrame({
            'account': [account],
            'last_scrapped': [current_time if downloaded_posts > 0 else 0],
            'total_posts': [total_posts],
            'new_posts': [new_posts],
            'downloaded_posts': [downloaded_posts],
            'reference_date': [current_time]
        })
        df = pd.concat([df, new_row], ignore_index=True)
        logger.info(f"Added new account to CSV: {account}")
    
    # Save the updated CSV
    df.to_csv(csv_file, index=False, sep=seperator)
    logger.info(f"CSV file updated successfully")

def read_accounts_from_csv():
    # Create base directory if it doesn't exist
    os.makedirs(config.base_dir, exist_ok=True)
    
    # Create CSV file if it doesn't exist
    if not os.path.exists(csv_file):
        df = pd.DataFrame(columns=['account', 'last_scrapped', 'total_posts', 'new_posts', 'downloaded_posts', 'reference_date'])
        df.to_csv(csv_file, index=False, sep=seperator)
        logger.info(f"Created new CSV file: {csv_file}")
        return []
    
    df = pd.read_csv(csv_file, sep=seperator)
    logger.info(f"Read {len(df)} accounts from CSV")
    return df['account'].tolist()  # Get 'account' column as list

def get_last_scraped_photo(account):
    # Create base directory if it doesn't exist
    os.makedirs(config.base_dir, exist_ok=True)
    
    # Create CSV file if it doesn't exist
    if not os.path.exists(csv_file):
        df = pd.DataFrame(columns=['account', 'last_scrapped', 'total_posts', 'new_posts', 'downloaded_posts', 'reference_date'])
        df.to_csv(csv_file, index=False, sep=seperator)
        logger.info(f"Created new CSV file: {csv_file}")
        return None
    
    df = pd.read_csv(csv_file, sep=seperator)
    
    # Check if account exists in CSV
    if account not in df['account'].values:
        logger.warning(f"Account {account} not found in CSV")
        return None
    
    last_scrapped = df.loc[df['account'] == account, 'last_scrapped'].values[0]
    
    # If last_scrapped is 0 or not a valid date string, return None
    if last_scrapped == 0 or not isinstance(last_scrapped, str):
        return None
    
    # Convert string date to datetime object
    try:
        return datetime.strptime(last_scrapped, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        logger.error(f"Invalid date format in CSV for {account}: {last_scrapped}")
        return None

def save_accounts_to_csv(following_list):
    # Create base directory if it doesn't exist
    os.makedirs(config.base_dir, exist_ok=True)
    
    # Read existing CSV if it exists
    if os.path.exists(csv_file):
        logger.info(f"CSV file exists: {csv_file}")
        df = pd.read_csv(csv_file, sep=seperator)
        existing_accounts = set(df['account'])
    else:
        df = pd.DataFrame(columns=['account', 'last_scrapped', 'total_posts', 'new_posts', 'downloaded_posts', 'reference_date'])
        existing_accounts = set()
        logger.info(f"Created new CSV file: {csv_file}")

    # Filter out existing accounts
    new_accounts = [acc for acc in following_list if acc not in existing_accounts]
    
    if new_accounts:
        # Create new rows for unique accounts
        new_rows = pd.DataFrame({
            'account': new_accounts,
            'last_scrapped': [0] * len(new_accounts),
            'total_posts': [0] * len(new_accounts),
            'new_posts': [0] * len(new_accounts),
            'downloaded_posts': [0] * len(new_accounts),
            'reference_date': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")] * len(new_accounts)
        })
        
        # Append new rows and save
        df = pd.concat([df, new_rows], ignore_index=True)
        df.to_csv(csv_file, sep=seperator, index=False)
        logger.info(f"Added {len(new_accounts)} new accounts to CSV")
    else:
        logger.info("No new accounts to add to CSV")

if __name__ == '__main__':
    # Set up logging for standalone execution
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("file_operations.log"),
            logging.StreamHandler()
        ]
    )
    
    # Test function
    save_accounts_to_csv([])
