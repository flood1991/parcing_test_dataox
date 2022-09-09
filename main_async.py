import aiohttp
import asyncio
from bs4 import BeautifulSoup
import re
from create_db import LocalSession, Flat


async def get_page_data(session, page):

    url = f"https://www.kijiji.ca/b-apartments-condos/city-of-toronto/page-{page}/c37l1700273"

    async with session.get(url=url) as response:
        response_text = await response.read()
        soup = BeautifulSoup(response_text.decode('utf-8'), 'html.parser')
        data = soup.findAll('div', class_='search-item')
        for list_obj in data:

            image = list_obj.find('div', class_='clearfix').find('img').get('data-src')
            beds = ' '.join(list_obj.find('span', class_='bedrooms').text.split()[1:])

            info_elements = list_obj.find('div', class_='info-container')

            title = info_elements.find('a', class_='title').text.strip()
            date = info_elements.find('span', class_='date-posted').string.replace('/', '-')
            city = info_elements.find('span', class_='').text.strip()
            description = info_elements.find('div', class_='description').text.strip()
            at_price = info_elements.find('div', class_='price').text.strip()
            currency = re.sub(r'[\d\w]', '', at_price)[0]
            price = re.sub(r'[A-Za-z$]', '', at_price)
            if price == ' ':
                price = at_price

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


async def gather_data():

    url = f"https://www.kijiji.ca/b-apartments-condos/city-of-toronto/c37l1700273"

    async with aiohttp.ClientSession() as session:
        async with session.get(url=url) as response:
            text = await response.read()
            soup = BeautifulSoup(text.decode('utf-8'), 'html.parser')
            count = soup.find('span', class_="resultsShowingCount-1707762110").text.split()[5]
            page_count = int(int(count) / 40) + 1
            tasks = []
            for page in range(1, page_count):
                task = asyncio.create_task(get_page_data(session, page))
                tasks.append(task)
            await asyncio.gather(*tasks)


def main():
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(gather_data())

main()
