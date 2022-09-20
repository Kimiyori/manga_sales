
import datetime
import asyncio
import re
import difflib
import uu
from .exceptions import NotFound
from manga_sales.data_scraping.meta import AbstractScraper
from manga_sales.data_scraping.dataclasses import Content
from bs4 import BeautifulSoup
import uuid


class OriconScraper(AbstractScraper):

    _URL = 'https://www.oricon.co.jp/rank/obc/w/'
    _SEARCH_URL = 'https://www.mangaupdates.com/series.html?search='
    _NUMBER_PAGES = 4

    def __init__(self, session) -> None:
        super().__init__(session)

    def _get_rating(self, item):
        try:
            rating = item.find('p', {'class': 'num'}).text
            rating = int(rating)
        except (AttributeError, ValueError):
            return 0
        return rating

    def _get_volume(self, item):
        try:
            list = item.find('h2', {'class': 'title'}).text.split(' ')
        except AttributeError:
            return 0
        if len(list) == 0:
            return 0
        volume = None
        for item in list:
            try:
                volume = int(item)
                break
            except ValueError:
                continue
        return volume

    def _get_release_date(self, item):
        text = item.find('ul', {'class': 'list'}).contents[3].text
        raw_data = text.split('：')[-1]
        data = re.match(
            r'(?P<year>\d{4})\w(?P<month>\d{2})', raw_data, re.MULTILINE)
        date = datetime.date(int(data['year']), int(
            data['month']), 1)
        return date

    def _get_sold_amount(self, item):
        try:
            text = item.find('ul', {'class': 'list'}).contents[7].text
            data = text.split('：')[-1][:-1]
        except AttributeError:
            return 0
        return int(data.replace(',', ''))

    async def fetch(self, url, expect_bs=True):
        response = await self.session.fetch(url, expect_bs)
        return BeautifulSoup(response, 'html.parser') if expect_bs else response

    async def _get_title(self, item):

        def get_most_similar_title(original_name, link):

            items = link.find_all(
                'div', {'class': 'col-12 col-lg-6 p-3 text'})

            titles = {}

            for item in items:
                item = item.find('div', {'class': 'text'})
                titles[item.find('b').text] = item.find(
                    'a')['href']
            most_similar = difflib.get_close_matches(
                original_name, titles.keys())
            return titles[most_similar[0]] if most_similar else titles[list(titles.keys())[0]]

        split_name = item.find(
            'h2', {'class': 'title'}).text.split(' ')
        japanese_name = ' '.join(
            x for x in split_name[:-1]) if len(split_name) > 1 else split_name[0]

        mangau_list = await self.fetch(self._SEARCH_URL+japanese_name)
        mangau_item_link = get_most_similar_title(
            japanese_name, mangau_list)
        title_page = await self.fetch(mangau_item_link)
        english_name = title_page.find(
            'span', {'class': 'releasestitle tabletitle'}).text

        return english_name, title_page

    def _get_authors(self, item):
        try:
            authors_tag = item.find(
                'b', text='Author(s)').parent.find_next_sibling('div')
            authors_list = [
                author.text for author in authors_tag.find_all('u')]
        except AttributeError:
            return []
        return authors_list

    def _get_publishers(self, item):
        try:
            publishers_tag = item.find(
                'b', text='Original Publisher').parent.find_next_sibling('div')
            publishers = [
                publisher.text for publisher in publishers_tag.find_all('u')]
        except AttributeError:
            return []
        return publishers

    async def _get_image(self, item):
        try:
            img_url = item.find('p', {'class': 'image'}).find('img').get('src')
            if img_url is None:
                return None
        except AttributeError:
            return None
        extension = re.search(r'.(\w+)$', img_url).group(1)
        name = f'{uuid.uuid4()}.{extension}'
        binary_image = await self.fetch(img_url, expect_bs=False)
        return name, binary_image

    async def retrieve_data(self, url):
        data = await self.fetch(url)
        list_items = data.find_all('section', {'class': 'box-rank-entry'})
        for item in list_items:
            rating: int = self._get_rating(item)
            image_name, image = await self._get_image(item)
            name, data_url = await self._get_title(item)
            authors = self._get_authors(data_url)
            publishers = self._get_publishers(data_url)
            volume = self._get_volume(item)
            release = self._get_release_date(item)
            sold = self._get_sold_amount(item)
            content = Content(name, volume, image_name, image, authors,
                              publishers, release, rating, sold)
            self.rating_list.append(content)

    async def get_data(self, date):
        pages = [self._URL + date +
                 f'/p/{x}/' for x in range(1, self._NUMBER_PAGES)]
        async with self.session:
            tasks = [asyncio.create_task(
                self.retrieve_data(page)) for page in pages]
            await asyncio.gather(*tasks)

        return self.rating_list

    async def find_latest_date(self, operator):
        async with self.session:
            date = None
            delta, count_days = 0, 0
            while not date and count_days <= 7:
                guess_date = operator(
                    datetime.date.today(), datetime.timedelta(days=delta)
                )
                url = self._URL+guess_date.strftime('%Y-%m-%d')+'/'
                try:
                    await self.session.fetch(url)
                except NotFound:
                    delta += 1
                    count_days += 1
                return guess_date
        return None
