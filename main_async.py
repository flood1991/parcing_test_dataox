import aiohttp
import asyncio
from bs4 import BeautifulSoup
import re
from create_db import LocalSession, Flat
import warnings
import dateparser
from time import sleep

warnings.filterwarnings(
    "ignore",
    message="The localize method is no longer necessary, as this time zone supports the fold attribute",
)


def db_write(image, title, date,
             city, beds, description,
             currency, price):

    with LocalSession() as db_session:
        flat = Flat(img_link=image,
                    title=title,
                    date=date,
                    city=city,
                    beds=beds,
                    description=description,
                    currency=currency,
                    price=price)
        db_session.add(flat)
        db_session.commit()


def get_info_from_page(response_text):
    soup = BeautifulSoup(response_text.decode('utf-8'), 'html.parser')
    data = soup.findAll('div', class_='clearfix')[1:]
    for list_obj in data:
        image = list_obj.find('img').get('data-src')
        if image is None:
            image = "No image"
        title = list_obj.find('a', class_='title').text.strip()
        text_date = list_obj.find('span', class_='date-posted').text
        date = dateparser.parse(text_date).strftime('%d-%m-%y')
        city = list_obj.find('span', class_='').text.strip()
        if list_obj.find('span', class_='bedrooms') is not None:
            beds = ' '.join(list_obj.find('span', class_='bedrooms').text.split()[1:])
        description = ' '.join(list_obj.find('div', class_='description').text.split())
        at_price = list_obj.find('div', class_='price').text.strip()
        currency = re.sub(r'[\d\w]', '', at_price)[0]
        price = re.sub(r'[A-Za-z$]', '', at_price)
        if price == ' ':
            price = at_price
        db_write(image, title, date,
                 city, beds, description,
                 currency, price)
        print("done")


async def get_page_data(session, page):

    url = f"https://www.kijiji.ca/b-apartments-condos/city-of-toronto/page-{page}/c37l1700273"
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
    }
    async with session.get(url=url, headers=headers) as response:
        response_text = await response.read()
        get_info_from_page(response_text)


async def gather_data():

    url = f"https://www.kijiji.ca/b-apartments-condos/city-of-toronto/c37l1700273"
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
    }
    tasks = []
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, headers=headers) as response:
            text = await response.read()
            soup = BeautifulSoup(text.decode('utf-8'), 'html.parser')
            count = soup.find('span', class_="resultsShowingCount-1707762110").text.split()[5]
            page_count = int(int(count) / 40) + 1
        for page in range(1, page_count):
            task = asyncio.create_task(get_page_data(session, page))
            tasks.append(task)
        await asyncio.gather(*tasks)


def main():
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(gather_data())


if __name__ == "__main__":
    main()
