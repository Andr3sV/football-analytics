# Football Analytics

This repo includes a Scrapy pipeline to collect first-division player data from Transfermarkt.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

Set a realistic USER_AGENT to reduce the chance of being blocked. You can pass season id (e.g., 2024) and a competitions file.

```bash
scrapy crawl players -s USER_AGENT="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36" \
  -a season=2024 \
  -a competitions_file=prime_players/competitions.json \
  -O players.jsonl
```

- competitions list lives in `prime_players/competitions.json` and includes codes like `ES1`, `GB1`, `IT1`, etc.
- output is JSONL with one player per line, including profile link, biographical data, contract info, agency, foot, kit brand, social links, and youth/training clubs.

## Notes

- This pipeline is inspired by community scrapers like `transfermarkt-scraper` and `Transfermarkt-Scraper`.
- Respect website terms and crawl responsibly with throttling and delays.
