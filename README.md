# iTunes Store App Review Scraper

Install with pip:

```
pip install git+git://github.com/mvoran/iTunesAppReviewScraper.git@v1.0.0
```

Import it as a module:

```
from iTunesAppReviewScraper import iTunesScraper
```

Run it with:

```
iTunesScraper.get_reviews(app_id, [base_path], [country])
```

`app_id` == the ID of the app you wish to scrape
  - To find the app_id of an app right click on the app icon in the iTunes store, then click on Copy Link
  - The link will have a form like this: `https://itunes.apple.com/us/app/{app name}/id{app_id}?mt=8`

`base_path` == the (optional) location where iTunesScraper will write CSV files containing app review data
  - **NOTE**: iTunesScraper **will not** check to see if base_path exists
  - **NOTE**: I recommend that you write to CSV in most cases, except if you are scraping only a single country
or are scraping an app with a limited number of reviews. In that case you can skip the copy to CSV and return results
directly to memory
	
`country` == the country abbreviation or ID of the country storefront you want to scrape
  - See [this](https://affiliate.itunes.apple.com/resources/documentation/linking-to-the-itunes-music-store/#appendix)
for a complete list. If `country` is not used then the tool will scrape all reviews from all countries

The return value is a `list` (or `dict` of `lists`) of `dicts` with the following format:

```
{
  'date': 'Sep 04, 2011',
  'stars': '5',
  'text': 'This app is really fantastic for plenty of reasons.',
  'title': 'A fantastic app!',
  'username': 'AyyLmao123',
  'version': '2.2'
}
```

Inspired by:

http://blogs.oreilly.com/iphone/2008/08/scraping-appstore-reviews.html

https://github.com/alihussain5/itunes-feedback-scraper/
