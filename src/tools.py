# =======================================================================================
#!/usr/bin/env python3
# Filename: tools.py
# Description: Re-usable functions/methods
# Author: Henin Roland Karkada <henin.roland@gmail.com>
# Python Environment - Python3
# Usage: To be used as a module
# ========================================================================================

# Standard modules
import configparser
import logging
import pymongo
import re

# Standard packages
from datetime import datetime

# LOCAL_RUN should be set to False always in production
#LOCAL_RUN = True
LOCAL_RUN = False

# Basic logging to be used for printing to console, level is set to DEBUG and can be used to write logs to files as well
try:
    logging.basicConfig(format="[%(asctime)s].%(msecs)03d %(levelname)s: "
                        "[%(name)s: %(filename)s:: %(funcName)s(): %(lineno)s] %(message)s")
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    config = configparser.ConfigParser()
    config.read('config.ini')

    if LOCAL_RUN:
        client = pymongo.MongoClient()

    else:
        logger.info("Into LOCAL_RUn False")
        mongo_username = config['mongodb']['user']
        mongo_password = config['mongodb']['password']

        mongo_host = "{}:27017".format(config['mongodb']['host'])
        client = pymongo.MongoClient(mongo_host)
    db = client.rss_articles

    logger.info("Creating DB succcessful")

except Exception as error:
    print("Logger error: {}".format(error))

# def filter_tags(tags):
#
#     if tags:
#         filtered_tags = {re.sub('[^0-9A-Za-z]', ' ', tag).lower().strip()
#                          for tag in tags}
#         filtered_tags = list({a_tags.replace('_', ' ')
#                               for a_tags in filtered_tags})
#     else:
#         filtered_tags = []
#     return filtered_tags

def update_mongo(result,
                 provider):
    """
    Check if the entry exists for the title, if not insert into MongoDB items collection
    :param result: Article JSON
    :param provider: Provider of the data
    :return: None
    """
    logger.info("Inserting the item into {} ....".format(provider))
    try:
        title = result.get("title", "").strip()
        description = result.get("description", "").strip()
        rss_categories = result.get("rss_categories", "")
        provider = result.get("provider", "")
        result["title"] = title
        result["description"] = description

        logger.info("Inserting provider: `{}` category: `{}` title: `{}`: datetime: `{}`".format(provider,
                                                                                                 rss_categories,
                                                                                                 title,
                                                                                                 datetime.now()))
        title = result.get('title', "").strip()
        description = result.get('description', "").strip()
        # Insert the Data into Mongo
        db.items.update({"title": title,
                         "description": description},
                        {'$set': result},
                        upsert=True)

    except Exception as error:
        logger.error(error)
