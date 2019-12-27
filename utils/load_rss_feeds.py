import requests

# Used to import the RSS feeds into the DB. Once in the DB the RSS feeds will be updated during a cron.

BASE_URL = 'https://us-central1-media-voice-applications.cloudfunctions.net'
# Endpoint for inserting feed into DB
DOWNLOAD_RSS_URL = "{0}/download_rss".format(BASE_URL)

path_to_rss_list = "/Users/milanarezina/Desktop/rss_feeds.txt"

with open(path_to_rss_list, 'r') as feeds:
    for feed in feeds:
        feed = feed.rstrip()
        r = requests.post(DOWNLOAD_RSS_URL, json={'rss_url': feed})

        if r.status_code == 500:
            print(f"Failed inserting: {feed}")
        else:
            print(f"Success Inserting: {feed}")
