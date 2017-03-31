import requests
import xml.etree.ElementTree as ET
import re
import dateparser
import pandas as pd

from itunes_app_review_scraper.config import Config

basepath = None

class iTunesScraper(object):
    @classmethod
    def _request_itunes(cls, app_id, store_id, page):
        headers = {'X-Apple-Store-Front': Config.STORE_FRONT.format(store_id=store_id), 'User-Agent': Config.USER_AGENT}

        r = requests.get(Config.URL.format(app_id=app_id, page=page), headers=headers)

        if r.status_code != 200:
            raise RuntimeError('Failed to get data for {}: {}'.format(store_id, r.status_code))

        return r.content

    @classmethod
    def _parse_itunes_xml(cls, data):
        reviews = []

        try:
            root = ET.fromstring(data)
        except:
            return reviews

        for node in root.findall(Config.REVIEW_NODE, Config.NAMESPACE):
            review = {}

            star_data = node.find(Config.STAR_CHILD, Config.NAMESPACE)
            text_data = node.find(Config.TEXT_CHILD, Config.NAMESPACE)
            review_metadata = node.findall(Config.METADATA_CHILD, Config.NAMESPACE)

            review['title'] = review_metadata[0][0].text
            
            #in most country storefronts the stars are listed as numbers, e.g., "5 stars"
            #but in SE, DE and AT the numbers are spelled out, e.g., "zwei stahlen"
            try:
                review['stars'] = re.search(r'\d', star_data.get('alt')).group()
            except:
                word = re.search(r'[\w]{2,4}',star_data.get('alt'), re.UNICODE).group()
                review['stars'] = Config.NUMBERS[word]
                
            review['text'] = text_data.text

            #usernames are usually in the first group (review_metadata[1][0][0])
            #but some CJK usernames are in the second group (review_metadata[1][0])
            try:
                review['username'] = review_metadata[1][0][0].text.strip()
            except:
                try:
                    review['username'] = review_metadata[1][0].text.strip()
                except:
                    review['username'] = 'UNPARSABLE'
                

            version_date_data = review_metadata[1][0].tail

            version = Config.VERSION_RE.search(version_date_data)

            if version:
                review['version'] = version.group()
            else:
                review['version'] = None

            #lots of date formats to manage 
            date = Config.DATE_RE.search(version_date_data)
            date_euro = Config.DATE_EURO_RE.search(version_date_data)
            date_nl = Config.DATE_NL_RE.search(version_date_data)
            date_br = Config.DATE_BR_RE.search(version_date_data)
            date_gb = Config.DATE_GB_RE.search(version_date_data)
            date_ru = Config.DATE_RU_RE.search(version_date_data)
            date_kr = Config.DATE_KR_RE.search(version_date_data)

            if date:
                review['date'] = dateparser.parse(date.group())      #since months are spelled out dateparser can handle dates without specifying order
            elif date_euro:
                review['date'] = dateparser.parse(date_euro.group()) #since months are spelled out dateparser can handle dates without specifying order
            elif date_nl:
                review['date'] = dateparser.parse(date_nl.group(), settings={'DATE_ORDER': 'DMY'})
            elif date_br:
                review['date'] = dateparser.parse(date_br.group(), settings={'DATE_ORDER': 'DMY'})
            elif date_gb:
                review['date'] = dateparser.parse(date_gb.group())   #since months are spelled out dateparser can handle dates without specifying order
            elif date_ru:
                review['date'] = dateparser.parse(date_ru.group(), settings={'DATE_ORDER': 'DMY'})
            elif date_kr:
                review['date'] = dateparser.parse(date_kr.group(), settings={'DATE_ORDER': 'YMD'})
            else:
                review['date'] = review_metadata[1][0].tail

            reviews.append(review)

        return reviews

    @classmethod
    def _get_all_pages(cls, app_id, store_id):
        reviews = []
        page = 0

        while 1:
            reviews_xml = cls._request_itunes(app_id, store_id, page)
            reviews_parsed = cls._parse_itunes_xml(reviews_xml)

            if not reviews_parsed:
                break

            reviews += reviews_parsed
            page += 1

            global basepath
            if not basepath is None:
              filename = str(store_id) + '_' + str(page).zfill(4) + '.csv'
              pdwrite = pd.DataFrame(reviews)
              pdwrite['text'] = pdwrite['text'].str.replace('\r\n', '')
              pdwrite.to_csv(basepath + filename, sep='|', quotechar='^', lineterminator='\n', encoding='utf-8')

              masterfilename = 'AppStoreReviews_' + str(app_id) + '_PagesCopied.txt'
              ofile = open(basepath + masterfilename, 'a')
              ofile.write(str(store_id) + '\t' + str(page).zfill(4) + '\n')
              ofile.close()
                        
              reviews=[] #reset the reviews list so that each page is written to only one csv file

        return reviews

    @classmethod
    def _get_all_countries(cls, app_id):
        reviews = {}

        for country, store_id in Config.COUNTRIES.items():
            reviews[country] = cls._get_all_pages(app_id, store_id)

        return reviews

    @classmethod
    def _get_reviews_country(cls, app_id, country='US'):
        if len(country) != 2 and len(country) != 6:
            raise ValueError('Either use a country code or a store id')

        if len(country) == 2:
            if country.upper() not in Config.COUNTRIES:
                raise ValueError('{} is not a valid country'.format(country))

            country = Config.COUNTRIES[country]

        if len(country) == 6:
            if country not in Config.COUNTRIES.values():
                raise ValueError('{} is not a valid store id'.format(country))

        reviews = cls._get_all_pages(app_id, country)

        return reviews

    @classmethod
    def get_reviews(cls, app_id, base_path=None, country=None):
        global basepath
        basepath = base_path
        if country is None:
            return cls._get_all_countries(app_id)

        return cls._get_reviews_country(app_id, country)
