import requests
import re
from create_db import LocalSession, Flat
from bs4 import BeautifulSoup


def main():
    url = f"https://www.kijiji.ca/b-apartments-condos/city-of-toronto/c37l1700273"
    response = requests.get(url=url)
    soup = BeautifulSoup(response.text, 'html.parser')
    count = soup.find('span', class_="resultsShowingCount-1707762110").text.split()[5]
    page_count = int(int(count) / 40) + 1
    for page in range(1, page_count):
        url = f"https://www.kijiji.ca/b-apartments-condos/city-of-toronto/page-{page}/c37l1700273"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        data = soup.findAll('div', class_='search-item')
        for list_obj in data:
            image = list_obj.find('div', class_='clearfix').find('img').get('data-src')

            info_elements = list_obj.find('div', class_='info-container')
            title = info_elements.find('a', class_='title').text.strip()
            date = info_elements.find('span', class_='date-posted').string.replace('/', '-')
            city = info_elements.find('span', class_='').text.strip()
            beds = ' '.join(list_obj.find('span', class_='bedrooms').text.split()[1:])
            description = info_elements.find('div', class_='description').text.strip()
            at_price = info_elements.find('div', class_='price').text.strip()
            currency = re.sub(r'[\d\w]', '', at_price)[0]
            price = re.sub(r'[A-Za-z$]', '', at_price)
            if price == ' ':
                price = at_price

            # with LocalSession() as db_session:
            #     flat = Flat(img_link=image,
            #                 title=title,
            #                 date=date,
            #                 city=city,
            #                 beds=beds,
            #                 description=description,
            #                 currency=currency,
            #                 price=price)
            #     db_session.add(flat)
            #     db_session.commit()


main()
