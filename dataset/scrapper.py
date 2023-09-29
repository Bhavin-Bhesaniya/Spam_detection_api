import requests
from bs4 import BeautifulSoup
import pandas as pd

websites = [
    {"url": "https://selzy.com/en/blog/spam-email-examples/", "tag_names": ["h3"]},
    {"url": "https://terranovasecurity.com/top-examples-of-phishing-emails/", "tag_names": ["strong"]},
    {"url": "https://www.smscountry.com/blog/spam-words-list/", "tag_names": ["td"]},
    {"url": "https://www.jooksms.com/blog/10-examples-of-spam-text-messages/", "tag_names": ["li", "em"]},
]

# Function scrape website and return DataFrame
def scrape_website(url, tag_names):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Initialize an empty list to store data
        data = []

        # Iterate through the tag names and scrape data for each
        for tag_name in tag_names:
            spam_tags = soup.find_all(tag_name)  # Use the specified tag_name
            spam_messages = [tag.get_text() for tag in spam_tags]
            data.extend(spam_messages)

        # Create DataFrame from the scraped data
        spam_df = pd.DataFrame({'target': [1] * len(data), 'text': data})
        return spam_df
    return None



# Initialize empty DataFrame to store combined data
combined_df = pd.DataFrame(columns=['target', 'text'])

# Iterate through the websites and scrape data
for website_info in websites:
    url = website_info["url"]
    tag_names = website_info["tag_names"]
    df = scrape_website(url, tag_names)
    if df is not None:
        combined_df = pd.concat([combined_df, df], ignore_index=True)

# Shuffle combined DataFrame
combined_df = combined_df.sample(frac=1).reset_index(drop=True)

# Save combined data to a CSV file
combined_df.to_csv('zcombined_scrapper_data.csv', index=True)
print("Data has been saved to 'combined_data.csv'.")

csv1 = pd.read_csv('zcombined_scrapper_data.csv', index_col=0)
csv2 = pd.read_csv('zclean_spamsms.csv', index_col=0)
csv3 = pd.read_csv('zspam_assassin.csv', index_col=0)
combined_df = pd.concat([csv1, csv2, csv3], ignore_index=True)
combined_df.to_csv('zfinaldataset.csv', index=False)