import argparse
import os
import urllib.request
from datetime import datetime

from bs4 import BeautifulSoup
from django.utils import feedgenerator


def make_feed(username, filename=None, aggregate_feed=None):
    if aggregate_feed:
        feed = aggregate_feed
    else:
        feed = feedgenerator.Rss201rev2Feed(
            title=f'Twitter @{username}',
            link=f'https://twitter.com/{username}',
            description=f'Tweets by @{username}',
        )

    with urllib.request.urlopen(f'https://twitter.com/{username}') as f:
        data = f.read()
    soup = BeautifulSoup(data, features='html5lib')

    for tweet in soup.find_all('div', class_='tweet'):
        text = tweet.find('div', class_='js-tweet-text-container').get_text(' ')
        if aggregate_feed:
            text = f'@{username}: {text}'
        relative_permalink = tweet.find('a', class_='js-permalink')['href']
        link = 'https://twitter.com' + relative_permalink
        timestamp = int(tweet.find(
            'span', class_='js-short-timestamp')['data-time'])

        feed.add_item(
            title=text,
            link=link,
            description=str(tweet),
            author=f'@{username}',
            pubdate=datetime.fromtimestamp(timestamp),
        )

    if filename:
        with open(filename, 'wb') as f:
            feed.write(f, encoding='utf-8')


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--aggregate-file')
    parser.add_argument('-u', '--username', action='append', required=True)
    parser.add_argument('-d', '--output-dir', default=os.getcwd())

    return parser.parse_args()


def main():
    args = parse_args()

    aggregate_feed = None
    if args.aggregate_file:
        aggregate_feed = feedgenerator.Rss201rev2Feed(
            title='Twitter',
            link='https://twitter.com/',
            description=f'Tweets from %d Twitter useres' % len(args.username),
        )

    for username in args.username:
        if aggregate_feed:
            make_feed(username, aggregate_feed=aggregate_feed)
        else:
            make_feed(username, filename=os.path.join(args.output_dir, f'{username}.xml'))

    if aggregate_feed:
        with open(args.aggregate_file, 'wb') as f:
            aggregate_feed.write(f, encoding='utf-8')


if __name__ == '__main__':
    main()
