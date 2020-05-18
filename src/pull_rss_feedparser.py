# =============================================================================
#!/usr/bin/env python3
# Filename: main.py
# Description: Python flask application to pull the latest articles from the RSS sites.
#   View the news articles, and check out similar articles related to it based on categories and tags
# Author: Henin Roland Karkada <henin.roland@gmail.com>
# Python Environment - Python3
# Usage: python pull_rss_feedparser.py
#
# Use Cases:
# 1. Pull the RSS data
#   => Input: client_info.py file which contains client info of all RSS sites info
#   => Output: Generic news article information pushed into Mongo DB rss_articles items collection.

#@ TODO
# Scope for Improvements:
# 1. Batch insertion of Mongo DB Items
# 2. Generic function to retrieve mongodb items
# 3. Eliminate Generic Exceptions, catch specific exceptions
# =============================================================================

# Standard packages
import feedparser
import re
import sys
import uuid

# Standard packages
from datetime import datetime
from newspaper import Article, ArticleException

# User created modules
import client_info

# User created packages
from tools import logger, update_mongo

spl_chr_pattern = re.compile("<[^<]+?>")

def parse_url(url):
    """
    Parse RSS XML URL and get the basic details
    :param url: RSS XML URL
    :param provider: Name of the Article provider
    :return: item
    """
    try:
        items = []
        column_list = ['title', 'summary', 'id', 'language', 'link', 'description', 'published', 'media_content', 'image']
        elements = feedparser.parse(url)
        elements = (element for element in elements.entries)
        if not elements:
            return []
        logger.info("Please wait, parsing through the RSS feeds........")
        for element_res in elements:
            item = {}
            for element in element_res:
                if element in column_list:
                    item[element] = element_res.get(element)
                    if 'media_content' in element_res:
                        item['image_url'] = element_res.media_content[0]['url']
                    else:
                        item['image_url'] = element_res.get('image')
            item = get_metadata_newspaper(item)
            # yield item
            if item:
                items.append(item)
        return iter(items)
    except Exception as error:
        logger.error(error)

def get_metadata_newspaper(item):
    """
    Use newspaper3k library to get more details like Image URL and other metadata
    :param item: Article data
    :return: item
    """
    try:
        if not item['link'] and not item['id']:
            return {}
        if item['link'] and item['link'] != "":
            article = Article(item['link'])
        else:
            article = Article(item['id'])

        try:
            article.download()
            article.parse()
        except ArticleException:
            try:
                article = Article(item['link'])
                article.download()
                article.parse()
            except:
                article = {}
        if article:
            if article.title:
                item['title'] = article.title
            if article.text:
                item['description'] = article.text
            if article.top_image:
                item['image_url'] = article.top_image
    except Exception as error:
        logger.error(error)

    return item

def update_metadata(item,
                    rss_cat,
                    provider):
    """
    Update the metadata of the content and structure the data to be pushed into DB
    :param item: Individual item
    :param rss_cat: Category of the article
    :param provider: Provider
    :return: result
    """
    try:
        title = item.get('title', '')
        description = item.get('description', '')

        #@TODO: Use compile
        description = re.sub(spl_chr_pattern, '', description)
        tags = []
        topics = []
        classifications = []

        if item.get('published'):
            publish_date = datetime.now()
            #publish_date = item.get('published').strftime('%d-%m-%Y')
        else:
            publish_date = datetime.now()

        # Update the dicitonary  RSS provider data_point
        result = {}
        result['item_id'] = str(uuid.uuid4()) #hashlib.md5(title.encode('utf-8')).hexdigest()
        result['provider'] = provider
        result['language'] = "English"
        result['title'] = title
        result['description'] = description
        result['summary'] = item.get('summary')
        result['tags'] = tags
        result['topics'] = topics
        result['rss_categories'] = rss_cat
        result['image_url'] = item.get('image_url', '')
        result['link_url'] = item.get('link', '')
        result['classifications'] = classifications
        result['publish_date'] = publish_date
        result['last_modified'] = datetime.now()
        return result
    except Exception as error:
        logger.error(error)


def pull_feeds(url,
               provider,
               rss_category):
    """
    Pull feeds for an individual category specific Article
    :param url: Category based Provider URL link
    :param provider: Name of the Article Provider
    :param rss_category: Category of the articles
    :return: None
    """
    try:
        # Get provider from the config file
        items = parse_url(url)

        if items:
            # Loop through the items iterator object
            for item in items:
                # if no title or description skip the article
                if not item['title'] and item['description']:
                    continue
                # Update Metadata
                result = update_metadata(item,
                                          rss_category,
                                          provider)

                # Update Mongo DB
                update_mongo(result,
                             provider)
        else:
            logger.warning("Unable to pull items for `{}` in  `{}` category".format(provider, rss_category))

    except Exception as error:
        logger.error(error)


def fetch():
    json_data_client = client_info.CLIENTS
    if not json_data_client:
        logger.warning("RSS client info is empty. Check the client_info.py file")
        sys.exit(1)

    try:
        # Loop through the clients and individual category RSS site link
        for client in json_data_client:
            base_url = json_data_client[client]["base_url"]
            for category in json_data_client[client]["endpoints"]:
                url = base_url + json_data_client[client]["endpoints"][category]
                pull_feeds(url, client, category)

    except Exception as error:
        logger.error(error)

def main():
    # Fetch data from RSS sites
    fetch()

if __name__ == '__main__':
    main()
