import scrapy


class CompetitionItem(scrapy.Item):
	code = scrapy.Field()
	name = scrapy.Field()
	country = scrapy.Field()
	season = scrapy.Field()
	url = scrapy.Field()


class ClubItem(scrapy.Item):
	name = scrapy.Field()
	url = scrapy.Field()
	competition_code = scrapy.Field()
	season = scrapy.Field()
	country = scrapy.Field()
	city = scrapy.Field()
	founded = scrapy.Field()
	stadium = scrapy.Field()


class PlayerItem(scrapy.Item):
	relative_profile_url = scrapy.Field()
	full_name = scrapy.Field()
	date_of_birth = scrapy.Field()
	place_of_birth = scrapy.Field()
	country_of_birth = scrapy.Field()
	city_of_birth = scrapy.Field()
	age = scrapy.Field()
	height_cm = scrapy.Field()
	nationalities = scrapy.Field()
	position = scrapy.Field()
	agency = scrapy.Field()
	current_club = scrapy.Field()
	dominant_foot = scrapy.Field()
	club_joined_date = scrapy.Field()
	contract_expires = scrapy.Field()
	last_contract_extension = scrapy.Field()
	equipment_brand = scrapy.Field()
	social_links = scrapy.Field()
	training_clubs = scrapy.Field()
	season = scrapy.Field()
	competition_code = scrapy.Field()
	club_url = scrapy.Field()
