# Instagram Scraper with Anti-Ban Measures

This Instagram scraper is designed to avoid IP bans and rate limiting by implementing several anti-detection techniques.

## Features

- **Proxy Rotation**: Automatically rotates between multiple proxies to avoid IP bans
- **User-Agent Rotation**: Randomizes browser fingerprints to appear as different users
- **Human-like Behavior**: Implements random delays, scrolling patterns, and typing speeds
- **Rate Limit Detection**: Automatically detects when Instagram has rate-limited the scraper
- **Automatic Recovery**: Attempts to recover from rate limits by rotating proxies
- **Detailed Logging**: Comprehensive logging to track scraping progress and issues

## Setup

1. **Configure Proxies**:
   - Edit `config.py` to add your proxy servers
   - Set `use_proxies = True` to enable proxy rotation
   - Format: `"protocol://username:password@ip:port"`

2. **Instagram Credentials**:
   - Update `username` and `password` in `config.py`

3. **Install Dependencies**:
   ```
   pip install selenium beautifulsoup4 pandas requests
   ```

4. **ChromeDriver**:
   - Make sure you have ChromeDriver installed and in your PATH

## Usage

Run the main script to start scraping:

```
python ig_main.py
```

The script will:
1. Read account names from the CSV file
2. Log in to Instagram
3. Scrape posts from each account
4. Save metadata to JSON files
5. Update the CSV with scraping metrics

## Configuration Options

In `config.py`:

- `use_proxies`: Enable/disable proxy rotation
- `proxy_list`: List of proxy servers to use
- `rotate_user_agents`: Enable/disable user-agent rotation
- `user_agents`: List of user-agents to rotate between
- `min_delay`/`max_delay`: Range for random delays between actions
- `page_load_timeout`: Maximum time to wait for page loading

## Anti-Ban Strategies

This scraper implements several strategies to avoid detection:

1. **Random Delays**: Adds unpredictable pauses between actions
2. **Human-like Typing**: Types characters with random delays between keystrokes
3. **Natural Scrolling**: Mimics human scrolling patterns with occasional scrolling up
4. **Proxy Rotation**: Changes IP address after a certain number of requests
5. **User-Agent Rotation**: Changes browser fingerprint regularly
6. **WebDriver Cloaking**: Hides Selenium automation markers
7. **Rate Limit Detection**: Identifies when Instagram has flagged the scraper
8. **Automatic Recovery**: Implements backoff strategies when rate limited

## Troubleshooting

- **Persistent Rate Limiting**: Try increasing the delay between requests
- **Proxy Issues**: Verify your proxies are working and properly formatted
- **Login Failures**: Check your Instagram credentials and consider using a fresh account
- **Scraping Failures**: Review logs for specific error messages

## Logs

Logs are saved to:
- `scraper.log`: Main scraping activity
- `file_operations.log`: File and CSV operations

## Important Notes

- Instagram's terms of service prohibit scraping. Use responsibly and at your own risk.
- Using too many requests in a short time may still trigger rate limiting despite these measures.
- Consider implementing additional delays between scraping sessions. 
