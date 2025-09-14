import json
from urllib.parse import urljoin

import scrapy
from parsel import Selector
from dateutil import parser as dateparser

from prime_players.items import PlayerItem


COMPETITION_CODES = {
	# Spain, Portugal, France, Germany, Sweden, Belgium, Poland
	"ES1": "Spain - LaLiga",
	"PO1": "Portugal - Liga Portugal",
	"FR1": "France - Ligue 1",
	"L1": "Germany - Bundesliga",
	"SE1": "Sweden - Allsvenskan",
	"BE1": "Belgium - Pro League",
	"PL1": "Poland - Ekstraklasa",
	# South Korea, Saudi Arabia, Qatar
	"KOR1": "South Korea - K League 1",
	"SA1": "Saudi Arabia - Saudi Pro League",
	"QA1": "Qatar - Stars League",
	# Italy, Czech Republic, Norway, England, Scotland
	"IT1": "Italy - Serie A",
	"TS1": "Czech Republic - Fortuna Liga",
	"NO1": "Norway - Eliteserien",
	"GB1": "England - Premier League",
	"SC1": "Scotland - Premiership",
	# Brazil, Colombia, Switzerland, Turkey
	"BRA1": "Brazil - Serie A",
	"COL1": "Colombia - Categoria Primera A",
	"SW1": "Switzerland - Super League",
	"TR1": "Turkey - Super Lig",
}


class PlayersSpider(scrapy.Spider):
	name = "players"
	allowed_domains = ["transfermarkt.com", "www.transfermarkt.com"]

	def __init__(self, competitions_file=None, season=None, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.season = season
		self.competitions = list(COMPETITION_CODES.keys())
		if competitions_file:
			with open(competitions_file, "r", encoding="utf-8") as f:
				data = json.load(f)
				self.competitions = [c.get("code") for c in data if c.get("code")]

	def start_requests(self):
		for code in self.competitions:
			# Use standard competition URL structure
			if self.season:
				url = f"https://www.transfermarkt.com/startseite/wettbewerb/{code}/saison_id/{self.season}"
			else:
				url = f"https://www.transfermarkt.com/startseite/wettbewerb/{code}"
			yield scrapy.Request(url=url, callback=self.parse_competition, cb_kwargs={"competition_code": code})

	def parse_competition(self, response, competition_code):
		# Clubs table rows
		for club_row in response.css("table.items tbody tr"):  # main listing
			club_rel = club_row.css("td:nth-child(2) a::attr(href)").get()
			if not club_rel:
				continue
			club_url = urljoin(response.url, club_rel.split("?")[0])
			# Enforce season on club page when provided
			if self.season:
				sep = "&" if "?" in club_url else "?"
				club_url = f"{club_url}{sep}saison_id={self.season}"
			yield scrapy.Request(club_url, callback=self.parse_club, cb_kwargs={"competition_code": competition_code, "club_url": club_url})

		# Pagination safety (competitions usually one page)

	def parse_club(self, response, competition_code, club_url):
		# Find club name on the page to attach to players
		club_name = response.css("h1.data-header__headline-wrapper span::text").get()
		if not club_name:
			club_name = response.css("h1::text").get()
		if club_name:
			club_name = club_name.strip()

		# Find current squad player links
		for player_link in response.css("table.items tbody tr td:nth-child(2) a::attr(href)").getall():
			if "/profil/spieler/" in player_link or "/profil-spieler/" in player_link:
				player_url = urljoin(response.url, player_link.split("?")[0])
				yield scrapy.Request(player_url, callback=self.parse_player, cb_kwargs={"competition_code": competition_code, "club_url": club_url, "club_name": club_name})

	def parse_player(self, response, competition_code, club_url, club_name=None):
		item = PlayerItem()

		item["relative_profile_url"] = "/" + "/".join(response.url.split("/")[3:])
		item["competition_code"] = competition_code
		item["club_url"] = club_url
		item["season"] = self.season

		# Name
		full_name = response.css("h1.data-header__headline-wrapper span::text").get()
		if not full_name:
			full_name = response.css("h1::text").get()
		item["full_name"] = (full_name or "").strip()

		# Key facts box
		facts_html = "".join(response.css(".data-header__details, .info-table").getall())
		facts = Selector(text=facts_html)

		def text_after(label):
			sel = facts.xpath(f"//span[contains(., '{label}')]/parent::li/text()|//th[contains(., '{label}')]/following-sibling::td//text()")
			texts = [t.strip() for t in sel.getall() if t.strip()]
			return " ".join(texts) if texts else None

		# DOB and age
		dob_text = text_after("Date of birth") or text_after("Born")
		age_text = None
		if dob_text and ")" in dob_text and "(" in dob_text:
			try:
				age_text = dob_text.split("(")[-1].split(")")[0].replace("years", "").strip()
			except Exception:
				pass
		try:
			item["date_of_birth"] = dateparser.parse(dob_text.split("(")[0].strip(), fuzzy=True).date().isoformat() if dob_text else None
		except Exception:
			item["date_of_birth"] = None
		item["age"] = age_text

		# Birthplace
		birthplace = text_after("Place of birth")
		if birthplace and "," in birthplace:
			city, country = [x.strip() for x in birthplace.split(",", 1)]
			item["city_of_birth"] = city
			item["country_of_birth"] = country
		else:
			item["city_of_birth"] = birthplace
			item["country_of_birth"] = None
		item["place_of_birth"] = birthplace

		# Height
		height_text = text_after("Height")
		if height_text and "m" in height_text:
			try:
				meters = float(height_text.split("m")[0].strip().replace(",", "."))
				item["height_cm"] = int(round(meters * 100))
			except Exception:
				item["height_cm"] = None

		# Nationalities
		nationalities = facts.xpath("//span[contains(@class,'data-header__content') and contains(., 'Citizenship')]/following::li[1]//img/@alt | //th[contains(., 'Citizenship')]/following-sibling::td//img/@alt").getall()
		if not nationalities:
			nationalities = response.css("li.data-header__label:contains('Citizenship') + li img::attr(alt)").getall()
		item["nationalities"] = [n.strip() for n in nationalities if n.strip()]

		# Position
		position = text_after("Position") or text_after("Main position")
		item["position"] = position

		# Agency
		agency = text_after("Player agent") or text_after("Agent")
		item["agency"] = agency

		# Current club; prefer captured club_name
		current_club = club_name or text_after("Current club")
		item["current_club"] = current_club

		# Foot
		dominant_foot = text_after("Foot")
		item["dominant_foot"] = dominant_foot

		# Contract dates
		item["club_joined_date"] = text_after("Joined")
		item["contract_expires"] = text_after("Contract expires") or text_after("Contract until")
		item["last_contract_extension"] = text_after("Last contract extension")

		# Kit brand (may be under outfitter)
		item["equipment_brand"] = text_after("Outfitter") or text_after("Kit sponsor")

		# Social links
		social = []
		for a in response.css("a.socialmedia-icon::attr(href), a.socialmedia::attr(href)").getall():
			social.append(a)
		item["social_links"] = social

		# Training clubs (youth clubs on profile)
		training = facts.xpath("//th[contains(., 'Youth clubs')]/following-sibling::td//text()|//span[contains(., 'Youth clubs')]/parent::li//text()").getall()
		training = [t.strip() for t in training if t.strip() and t.strip() != ","]
		item["training_clubs"] = training

		# Attempt to find a performance data link to gather stats
		perf_href = None
		for href in response.css("a::attr(href)").getall():
			if href and ("leistungsdaten" in href or "performance" in href.lower()):
				perf_href = href
				break

		if perf_href:
			perf_url = urljoin(response.url, perf_href)
			# Keep the original item in meta to enrich with stats
			yield scrapy.Request(perf_url, callback=self.parse_player_stats, cb_kwargs={"item": item})
		else:
			yield item

	def parse_player_stats(self, response, item: PlayerItem):
		# Parse performance table with header mapping
		table = response.css("table.items")
		stats = []
		if table:
			headers = []
			for th in table.css("thead tr:last-child th"):
				parts = th.css("::attr(title), ::text").getall()
				text = " ".join([p.strip() for p in parts if p.strip()])
				headers.append(text)

			def normalize_header(s: str) -> str:
				s = s.strip().lower().replace("/", " ").replace("-", " ").replace("\xa0", " ")
				parts = [p for p in s.split() if p]
				return "_".join(parts) if parts else ""

			for row in table.css("tbody tr"):
				vals = []
				for td in row.css("td"):
					v = " ".join([t.strip() for t in td.css("::text").getall() if t.strip()])
					vals.append(v)
				if not any(vals):
					continue
				entry = {}
				for i in range(min(len(headers), len(vals))):
					key = normalize_header(headers[i]) or f"col_{i}"
					entry[key] = vals[i]
				stats.append(entry)
		item["season_stats"] = stats
		yield item


def _find_first_int(texts):
	for t in texts:
		try:
			return int(t)
		except Exception:
			continue
	return None


def _safe_int(val):
	try:
		return int(val) if val is not None else None
	except Exception:
		return None
