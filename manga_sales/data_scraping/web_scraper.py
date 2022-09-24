
import datetime
import asyncio
import re
import difflib
import uu
from .exceptions import BSError, NotFound
from manga_sales.data_scraping.meta import AbstractScraper
from manga_sales.data_scraping.dataclasses import Content
from bs4 import BeautifulSoup
import uuid


class OriconScraper(AbstractScraper):
    """
    Class for collecting data from Oricon
    """
    _URL: str = 'https://www.oricon.co.jp/rank/obc/w/'
    _SEARCH_URL: str = 'https://www.mangaupdates.com/series.html?search='
    _NUMBER_PAGES: int = 4

    def __init__(self, session) -> None:
        super().__init__(session)

    async def fetch(self,
                    url: str,
                    commands: list[str] | None = None,
                    bs: bool = True):
        """
        Method foe fetching given url

        Args:
            url:url from which exctract data
            commands: set fo commands that will be applied to response
            bs: return bs4 or pure response
        """
        response = await self.session.fetch(url, commands)
        return BeautifulSoup(response, 'html.parser') if bs else response

    def _get_rating(self, item: BeautifulSoup):
        try:
            rating = int(item.find('p', {'class': 'num'}).text)
        except (AttributeError, ValueError):
            return 0
        return rating

    def _get_volume(self, item: BeautifulSoup):
        volume = None
        try:
            list = item.find('h2', {'class': 'title'}).string.split(' ')
        except AttributeError:
            return volume
        # iterate over all space-separated words from the title and
        # catch the first integer (usually this will be the volume)
        for item in list:
            try:
                volume = int(item)
                break
            except ValueError:
                continue
        return volume

    def _get_release_date(self, item: BeautifulSoup):
        try:
            text = item.find('ul', {'class': 'list'}).find(
                lambda tag: tag.name == "li" and "発売日" in tag.string).string
        except AttributeError:
            return None
        # fetch year and month
        regex_date = re.search(
            r'(?P<year>\d{4})年(?P<month>\d{2})月',
            text)
        try:
            date = datetime.date(
                int(regex_date['year']),
                int(regex_date['month']),
                1) if regex_date else None
        except ValueError:
            return None
        return date

    def _get_sold_amount(self, item: BeautifulSoup):
        try:
            text = item.find('ul', {'class': 'list'}).find(
                lambda tag: tag.name == "li" and "推定売上部数" in tag.string).string
        except AttributeError:
            return 0
        regex_date = re.search(
            r'(?P<sold>[0-9,]+(?=部))',
            text)
        try:
            sold = float(regex_date['sold'].replace(
                ',', '.')) if regex_date else None
        except ValueError:
            return 0
        return sold

    async def _get_title(self, item: BeautifulSoup):

        def get_most_similar_title(original_name: str, link: BeautifulSoup):

            items = link.find_all(
                'div', {'class': 'col-12 col-lg-6 p-3 text'})

            titles: dict[str, str] = {}

            for item in items:
                item = item.find('div', {'class': 'text'})
                try:
                    titles[item.find('b').string] = item.find(
                        'a')['href']
                except KeyError:
                    continue
            most_similar = difflib.get_close_matches(
                original_name, titles.keys())
            # return link to most similar if they exist else return first in list fo titles
            return titles[most_similar[0]] if most_similar else titles[list(titles.keys())[0]]

        try:
            split_name = item.find(
                'h2', {'class': 'title'}).string.split(' ')
            japanese_name = ' '.join(
                x for x in split_name[:-1]) if len(split_name) > 1 else split_name[0]

            # get list fo titles from mangaupdates with search by japanese title
            mangau_list = await self.fetch(
                url=self._SEARCH_URL+japanese_name, commands=['content', 'read'])
            # find most similar title
            mangau_item_link = get_most_similar_title(
                japanese_name, mangau_list)
            title_page = await self.fetch(url=mangau_item_link, commands=['content', 'read'])
            english_name = title_page.find(
                'span', {'class': 'releasestitle tabletitle'}).string
        except AttributeError:
            raise BSError('Can\'t parse to find title name')
        return english_name, title_page

    def _get_authors(self, item: BeautifulSoup):
        try:
            authors_tag = item.find(
                'b', string='Author(s)').parent.find_next_sibling('div')
            authors_list = [
                author.string for author in authors_tag.find_all('u')]
        except AttributeError:
            return []
        return authors_list

    def _get_publishers(self, item: BeautifulSoup):
        try:
            publishers_tag = item.find(
                'b', string='Original Publisher').parent.find_next_sibling('div')
            publishers = [
                publisher.string for publisher in publishers_tag.find_all('u')]
        except AttributeError:
            return []
        return publishers

    async def _get_image(self, item: BeautifulSoup):
        try:
            img_url = item.find('p', {'class': 'image'}).find('img').get('src')
            if img_url is None:
                return None
        except AttributeError:
            return None
        extension = re.search(
            r'.(\w+)$', img_url).group(1)
        name = f'{uuid.uuid4()}.{extension}'
        binary_image = await self.fetch(img_url, ['read'], False)
        return name, binary_image

    async def retrieve_data(self, url: str):
        data = await self.fetch(url)
        list_items = data.find_all('section', {'class': 'box-rank-entry'})
        if not list_items:
            raise BSError('Fail to find class with titles list')
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

    async def get_data(self, date: str):
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
                    await self.fetch(url, bs=False)
                except NotFound:
                    delta += 1
                    count_days += 1
                    continue
                return guess_date
        return None
