"""
Web scraping module to get details of books and their category

__author__ = "chaitra hegde"
__version__ = "1.0"
__email__ = "chaihegde56@gmail.com"
"""

import requests
from bs4 import BeautifulSoup as Soup
import mysql.connector
from urlparse import urljoin
import re
import yaml


class Category:
    """
    Category parser
    """
    def __init__(self, url):
        self.url_link = url

    def get_category_details(self):
        """
        Get category_name and category_link
        :return category_list: list of category dict
        """
        session = requests.Session()
        try:
            response = session.request(url=self.url_link, method='GET')
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

        content = Soup(response.text, 'html.parser')
        category_div = content.find('div', {'class': 'side_categories'})
        category_ul = category_div.find('ul', {'class': 'nav nav-list'})
        category_ul = category_ul.findNext('ul')

        category_list = []
        category_dict = dict()

        for list in category_ul:
            anchor = list.find('a')

            if not isinstance(anchor, int):
                category_dict['category_link'] = urljoin(self.url_link, anchor.get('href'))
                category_dict['category_name'] = anchor.text.strip()
                category_list.append(category_dict.copy())
        return category_list


class Books():
    """
    Books details parser
    """
    def __init__(self, category_list):
        self.category_list = category_list

    def get_books_details(self, category_list, link):
        """
        Get books details like name, price rating etc
        :param category_list: list of category_name and link
        :param link: source link
        :return books_list: list of books dict
        """
        rating_dict = {'One': 1,
                       'Two': 2,
                       'Three': 3,
                       'Four': 4,
                       'Five': 5}

        availability_dict = {'In stock': 1}

        books_list = []
        books_dict = dict()
        session = requests.Session()

        for category in category_list:
            try:
                response = session.request(url=category['category_link'], method='GET')
            except requests.exceptions.RequestException as e:
                raise SystemExit(e)
            
            content = Soup(response.text, 'html.parser')
            book_details = content.findAll('article', {'class': 'product_pod'})
            for book_detail in book_details:
                book_image = book_detail.find('a')
                book_image = book_image.find('img')
                star = book_detail.find('p')
                name = book_detail.find('h3')
                price = book_detail.find('p', {'class': 'price_color'})
                availability = book_detail.find('p', {'class': 'instock availability'})

                books_dict['image_link'] = urljoin(link ,book_image.get('src').strip('../../../..'))
                books_dict['name'] = name.text
                books_dict['rating'] = rating_dict.get(star['class'][1])
                price = re.findall('\d*\.?\d+', price.text)
                books_dict['price'] = price[0]
                books_dict['availability'] = availability_dict.get(availability.text.strip(), 0)
                books_dict['category_name'] = category['category_name']
                books_dict['category_link'] = category['category_link']

                books_list.append(books_dict.copy())

        return books_list


def save_data(get_config_dict, books_list):
    """
    Save category and books details into mysql table
    :param books_list: list of books dict
    :return: None
    """
    mysql_creds = get_config_dict.get('mysql_creds')
    mydb = mysql.connector.connect(
          host=mysql_creds.get('host'),
          user=mysql_creds.get('user'),
          password=mysql_creds.get('password'),
          database=mysql_creds.get('database')
        )

    mycursor = mydb.cursor()

    # Save Category details
    for category in category_list:
        sql_query = "SELECT * FROM category where name = %s"
        mycursor.execute(sql_query, (category['category_name'],))
        record = mycursor.fetchone()
        if not record:
            sql_query = "INSERT INTO category (name, link) VALUES (%s, %s)"
            val = (category['category_name'], category['category_link'])
            mycursor.execute(sql_query, val)
            mydb.commit()

    # Save Books details
    for book in books_list:
        sql_query = "SELECT id FROM category where name = %s"
        mycursor.execute(sql_query, (book['category_name'],))
        category_record = mycursor.fetchone()

        sql_query = "SELECT * FROM books where name = %s"
        mycursor.execute(sql_query, (book['name'],))
        record = mycursor.fetchone()
        if not record:  # Insert Record
            sql_query = "INSERT INTO books (name, image_link, rating, price, availability, category_id)" \
                        " VALUES (%s, %s, %s, %s, %s, %s)"
            val = (book['name'], book['image_link'], book['rating'], book['price'], book['availability'], category_record[0])
        else:  # Update book details
            sql_query = "UPDATE books SET rating = %s, price = %s, availability = %s WHERE name = %s"
            val = (book['rating'], book['price'], book['availability'], book['name'])

        mycursor.execute(sql_query, val)
        mydb.commit()


def get_config_dict(cfg_file):
    """
    Parse the given config file
    :param cfg_file: Config file path
    :return: Config dict
    """
    try:
        with open(cfg_file, 'r') as cfgfile:
            cfg = yaml.safe_load(cfgfile)
        return cfg
    except IOError as ex:
        raise IOError("Error in reading config file: %s" % str(ex))


source_url = "http://books.toscrape.com/"

category = Category(source_url)
category_list = category.get_category_details()

book = Books(category_list)
books_list = book.get_books_details(category_list, source_url)

config_dict = get_config_dict('/home/chai/Desktop/config.yaml')
save_data(config_dict, books_list)

