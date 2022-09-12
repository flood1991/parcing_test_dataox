import requests
import re
from bs4 import BeautifulSoup
import dateparser
import warnings
from time import sleep
from googlesheets import GoogleSheets
from create_db import LocalSession, Flat

warnings.filterwarnings(
    "ignore",
    message="The localize method is no longer necessary, as this time zone supports the fold attribute",
)


def write_to_sheets(number, page, image,
                    title, date, city, beds,
                    description, currency, price):

    sheets = GoogleSheets()
    write_values = f"TestList!A{str(number+45*(page-1))}:H{str(number+45*(page-1))}"
    sheets.update_values(write_values, [[image], [title], [date],
                                        [city], [beds], [description],
                                        [currency], [price]], "Columns")
    sleep(0.8)


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


def main():

    url = f"https://www.kijiji.ca/b-apartments-condos/city-of-toronto/c37l1700273"
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
    }
    response = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    count = soup.find('span', class_="resultsShowingCount-1707762110").text.split()[5]
    page_count = int(int(count) / 40) + 1

    for page in range(1, page_count):
        url = f"https://www.kijiji.ca/b-apartments-condos/city-of-toronto/page-{page}/c37l1700273"
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
        }

        response = requests.get(url=url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        data = soup.findAll('div', class_='clearfix')[1:]

        for number, list_obj in enumerate(data, 2):
            image = list_obj.find('img').get('data-src')
            if image is None:
                image = "No image"
            title = list_obj.find('a', class_='title').text.strip()
            text_date = list_obj.find('span', class_='date-posted').text
            date = dateparser.parse(text_date).strftime('%d-%m-%y')
            city = list_obj.find('span', class_='').text.strip()
            beds = ' '.join(list_obj.find('span', class_='bedrooms').text.split()[1:])
            description = ' '.join(list_obj.find('div', class_='description').text.split())
            at_price = list_obj.find('div', class_='price').text.strip()
            currency = re.sub(r'[\d\w]', '', at_price)[0]
            price = re.sub(r'[A-Za-z$]', '', at_price)
            if price == ' ':
                price = at_price

            db_write(image,
                    title, date, city, beds,
                    description, currency, price)


'''      ***SAVE TO GOOGLE_SHEETS***
          
            write_to_sheets(number, page, image,
                            title, date, city, beds,
                            description, currency, price)
'''

if __name__ == "__main__":
    main()
