CLIENTS = {

    "news_au": {"base_url": "https://www.news.com.au/content-feeds/",
                "endpoints": {
                          "national": "latest-news-national",
                          "world": "latest-news-world",
                          "lifestyle": "latest-news-lifestyle",
                          "travel": "latest-news-travel",
                          "entertainment": "latest-news-entertainment",
                          "technology": "latest-news-technology",
                          "finance": "latest-news-finance",
                          "sport": "latest-news-sport"
                        },
                "parsing_type": "feedparser",
                "provider": "new_au"
                },
    "theage": {"base_url": "https://www.theage.com.au/rss/",
               "endpoints": {
                              "politics": "politics/federal.xml",
                              "world": "world.xml",
                              "lifestyle": "lifestyle.xml",
                              "national": "national.xml",
                              "technology": "technology.xml",
                              "business": "business.xml",
                              "sport": "sport.xml"
                            },
               "parsing_type": "feedparser",
               "provider": "theage"
               },
    "sbs": {"base_url": "https://www.sbs.com.au/",
            "endpoints": {
                          "world": "/news/topic/world/feed",
                        },
            "parsing_type": "feedparser",
            "provider": "sbs"
            }
}
