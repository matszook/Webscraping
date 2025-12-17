import scrapy
import re

class MoviesSpider(scrapy.Spider):
    name = "movies"
    allowed_domains = ["en.wikipedia.org"]
    start_urls = ["https://en.wikipedia.org/wiki/List_of_highest-grossing_films"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.seen_movies = set()
        self.max_items = 50  # Only yield top 50
        self.count = 0

    def parse(self, response):
        # Select all rows in the first wikitable
        rows = response.css("table.wikitable tbody tr")

        for row in rows:
            if self.count >= self.max_items:
                break  # stop after 50 items

            cells = row.css("td")
            if len(cells) < 3:
                continue  # skip header/malformed rows

            # Extract all text from each cell
            texts = ["".join(c.css("::text").getall()).strip() for c in cells]
            texts = [t for t in texts if t]

            # Extract title
            title = row.css("i a::text").get()
            if not title and texts:
                title = texts[0]
            if not title:
                continue
            title = title.strip()

            # Extract year
            year = next((t for t in texts if re.search(r"\d{4}", t)), None)
            if not year:
                continue
            year = re.sub(r"\[.*?\]", "", year).strip()

            # Extract worldwide gross
            gross = next((t for t in texts if "$" in t), None)
            if not gross:
                continue
            gross = re.sub(r"\[.*?\]", "", gross).strip()

            # Deduplicate
            key = (title, year)
            if key in self.seen_movies:
                continue
            self.seen_movies.add(key)

            # Yield cleaned item
            yield {
                "title": title,
                "year": year,
                "worldwide_gross": gross
            }

            self.count += 1