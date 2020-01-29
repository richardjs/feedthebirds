import argparse
import os
import urllib.request
from datetime import datetime

from bs4 import BeautifulSoup
from django.utils import feedgenerator


args = None


def make_feed(username, filename):
    feed = feedgenerator.Rss201rev2Feed(
        title=f'Twitter @{username}',
        link=f'https://twitter.com/{username}',
        description=f'Tweets by @{username}',
    )

    with urllib.request.urlopen(f'https://twitter.com/{username}') as f:
        data = f.read()
    soup = BeautifulSoup(data, features='html5lib')

    for tweet in soup.find_all('div', class_='tweet'):
        text = tweet.find('div', class_='js-tweet-text-container').get_text()
        relative_permalink = tweet.find('a', class_='js-permalink')['href']
        link = 'https://twitter.com' + relative_permalink
        timestamp = int(tweet.find('span', class_='js-short-timestamp')['data-time'])

        feed.add_item(
            title=text,
            link=link,
            description=str(tweet),
            author=f'@{username}',
            pubdate=datetime.fromtimestamp(timestamp),
        )

    with open(filename, 'wb') as f:
        feed.write(f, encoding='utf-8')


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username', action='append')
    parser.add_argument('-d', '--output-dir', default=os.getcwd())

    global args
    args = parser.parse_args()


if __name__ == '__main__':
    parse_args()
    for username in args.username:
        # since we're using the username to build paths, test for
        # alphanumeric (since Twitter handles should be anyway)
        if not username.isalnum():
            print(f'WARNING: skipping {username} -- not alphanumeric')

        make_feed(username, os.path.join(args.output_dir, username+'.xml'))
