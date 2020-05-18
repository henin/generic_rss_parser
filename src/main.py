# =============================================================================
#!/usr/bin/env python3
# Filename: main.py
# Description: Python flask application to pull the latest articles from the RSS sites.
#   View the news articles, and check out similar articles related to it based on categories and tags
# Author: Henin Roland Karkada <henin.roland@gmail.com>
# Python Environment - Python3
# Usage: python main.py
#
# Use Cases:
# 1. Pull the RSS data
#   => Input:
#   => Output:
# 2. View all articles based on category

#@ TODO
# Scope for Improvements:
# 1. Batch insertion of Mongo DB Items
# 2. Pretty UI
# 3. Multi-threading
# 4. Use of generators

# =============================================================================

# Standard packages
from flask import Flask, request, jsonify, render_template, session, redirect, url_for

# User defined packages
from tools import logger, db

# User created modules
import pull_rss_feedparser

# Initiate the app
app = Flask(__name__)
app.secret_key = 'dljsaklqk24e21cjn!Ew@@dsa5'


@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('landing_page.html')


@app.route('/pull_feeds', methods=['POST', 'GET'])
def pull_feeds():
    try:
        pull_rss_feedparser.fetch()
        return jsonify({"Finished pulling all data!!!"})

    except Exception as error:
        logger.error(error)


@app.route('/recommendation', methods=['POST', 'GET'])
def view_articles():
    return render_template('articles.html')


@app.route('/get_recommendation', methods=['POST', 'GET'])
def recommendation():
    try:
        category = request.args.get('categories')
        filter_type = request.args.get('filter_type')
        filter_value = request.args.get('filter_value')

        results = get_recommendation(category, filter_type, filter_value)
        return jsonify(results)
    except Exception as error:
        logger.error(error)

def get_recommendation(category,
                       filter_type=None,
                       filter_value=None):
    """
    Get recommended articles
    :param category: Category from RSS type
    :param filter_type: Filter type
    :param filter_value: Filter value
    :return: RecommendedItems
    """
    try:
        if filter_type == 'tags' and filter_value and not category:
            query = {"summary": {"$regex": filter_value, "$options": 'i'}}
            results = list(db.items.find(query, {"_id": 0, "title": 1, "summary": 1, "link_url": 1}))
            return {"Similar Articles": results, "Chosen Tag": filter_value}

        elif filter_type == 'tags' and filter_value and category:
            query = {"summary": {"$regex": filter_value, "$options": "i"}, "rss_categories": category}
            results = list(db.items.find(query, {"_id": 0, "title": 1, "summary": 1, "link_url": 1}))
            return {"Similar Articles": results, "Chosen Tag": filter_value}
        #
        # elif filter_type == 'source' and filter_value:
        #     results = list(db.items.find({"rss_categories": category, "provider": "provider"},
        #                                  {"_id": 0, "title": 1, "summary": 1, "link_url": 1}))
        #     return {"Similar Articles": results, "Chosen Provider": provider, "Chosen Category": category}
        else:
            results = list(db.items.find({"rss_categories": category},
                                     {"_id": 0, "title": 1, "summary": 1, "link_url": 1}))
            return {"Similar Articles": results, "Chosen Category": category}

        return results
    except Exception as error:
        logger.error(error)

#if __name__ == '__main__':
    #pass