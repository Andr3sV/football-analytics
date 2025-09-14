BOT_NAME = "prime_players"

SPIDER_MODULES = ["prime_players.spiders"]
NEWSPIDER_MODULE = "prime_players.spiders"

# Obey robots.txt? Transfermarkt blocks bots; set to False to allow crawling tests.
ROBOTSTXT_OBEY = False

# Configure reasonable concurrency and throttling to be gentle
CONCURRENT_REQUESTS = 8
DOWNLOAD_DELAY = 1.5
CONCURRENT_REQUESTS_PER_DOMAIN = 8

DEFAULT_REQUEST_HEADERS = {
	"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
	"Accept-Language": "en",
}

# Enable AutoThrottle
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1.0
AUTOTHROTTLE_MAX_DELAY = 10.0
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0

# Pipelines
ITEM_PIPELINES = {
}

# Configure feed export via -O output.jsonl
FEED_EXPORT_ENCODING = "utf-8"

# USER_AGENT must be set on run via -s USER_AGENT="..." or here
USER_AGENT = None
