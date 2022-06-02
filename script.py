from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import pandas as pd
import numpy as np
from datetime import datetime

class ScraperHeureka():

    def __init__(self, url):
        self. url = url

    def open_driver(self):
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.driver.get(self.url)
        time.sleep(3)
        self.driver.find_element(by=By.XPATH, value='//*[@id="didomi-notice-agree-button"]').click()
        return self.driver

    def open_more_pages(self, x=5):
        while x > 0:
            try:
                self.driver.find_element(by=By.XPATH,
                                    value='*//a[@class="e-button e-button--medium e-button--simple c-pagination__button"]').click()
                time.sleep(0.5)
                x -= 1
            except:
                break

    def __open_all_offers(self):
        while True:
            try:
                self.driver.find_element(by=By.XPATH, value='*//div[@class="c-offers-list__wrapper"]/button').click()
                time.sleep(0.5)
            except:
                break

    def get_products_list(self):
        products = self.driver.find_elements(by=By.XPATH, value='*//h3[@class="c-product__title"]/a')
        self.products_list = []
        for i, product in enumerate(products):
            if 'graficke-karty' in product.get_attribute('href'):
                product_url = product.get_attribute('href')
                product_name = product.text
                self.products_list.append({
                    'product_name': product_name,
                    "url": product_url,
                    'price': '',
                    'shop_link': ''
                })
            else:
                product_url = product.get_attribute('href')
                product_name = product.text
                self.products_list.append({
                    'product_name': product_name,
                    "url": product_url,
                    'price': self.__get_price2(i),
                    'shop': self.__get_shop_name2(i)
                })
        return self.products_list

    def __get_offers_list(self, prices, shops, shop_links, product_list):
        self.offers_list = []
        for price, shop, shop_link in zip(prices, shops, shop_links):
            offer = {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'title': product_list['product_name'],
                'price': price,
                'shop': shop,
                'shop_link': shop_link
            }
            self.offers_list.append(offer)
        return self.offers_list


    def get_all_products(self, products_list):
        all_products = []
        for i in range(len(products_list)):
            if 'graficke-karty' in products_list[i]['url']:
                self.driver.get(products_list[i]['url'])
                self.__open_all_offers()

                prices = self.__get_price('*//a[@class="c-offer__price-box"]/span')
                if prices == []:
                    prices = self.__get_price('*//a[@class="c-offer-v4__price-box"]/span')
                    shops = self.__get_shop_name('*//img[@class="c-offer-v4__shop-logo e-image-with-fallback"]')
                    shop_links = self.__get_shop_link('*//a[@class="c-offer-v4__shop-logo-cont"]')
                else:
                    shops = self.__get_shop_name('*//img[@class="c-offer__shop-logo e-image-with-fallback"]')
                    shop_links = self.__get_shop_link('*//div[@class="c-offer__col c-offer__col--1 u-milli"]/a')

                offers_list = self.__get_offers_list(prices, shops, shop_links, products_list[i])
            else:
                offers_list = [{
                'date': datetime.now().strftime('%Y-%m-%d'),
                'title': products_list[i]['product_name'],
                'price': products_list[i]['price'],
                'shop': products_list[i]['shop'],
                'shop_link': products_list[i]['url']
            }]
            all_products += offers_list
        return pd.DataFrame(all_products)

    def __get_price(self, v):
        prices = self.driver.find_elements(by=By.XPATH, value=v)
        self.price_list = []
        for price in prices:
            try:
                price = price.text[:-2].replace(' ', '')
                price = int(price)
            except:
                price = np.nan
            self.price_list.append(price)
        return self.price_list

    def __get_shop_name(self, v):
        shops = self.driver.find_elements(by=By.XPATH, value=v)
        self.shop_list = []
        for shop in shops:
            self.shop_list.append(shop.get_attribute('alt'))
        return self.shop_list

    def __get_shop_link(self, v):
        shop_links = self.driver.find_elements(by=By.XPATH, value=v)
        self.shop_link_list = []
        for shop_link in shop_links:
            self.shop_link_list.append(shop_link.get_attribute('href'))
        return self.shop_link_list

    def save_df_to_csv(self, df, path):
        return df.to_csv(path, encoding='utf-8-sig')

    def __get_price2(self, i):
        price = self.driver.find_element(by=By.XPATH,
                            value=f'''*//div[@class="l-products__container c-product-list o-wrapper__overflowing@lteLine is-not-fetching"]
                                  /ul/li[{i+1}]/section/div/div/div[2]/div/a/span''')
        try:
            price = price.text[:-2].replace(' ', '')
            self.price = int(price)
        except:
            self.price = np.nan
        return self.price

    def __get_shop_name2(self, i):
        shop = self.driver.find_element(by=By.XPATH,
                            value=f'*//div[@class="l-products__container c-product-list o-wrapper__overflowing@lteLine is-not-fetching"]/ul/li[{i+1}]/section/div/div/div[2]/div/a[2]/span')
        self.shop = shop.text.split(' ')[-1]
        return self.shop



