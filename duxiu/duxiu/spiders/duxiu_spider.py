# -*- coding: utf-8 -*-
import scrapy
import time
from selenium import webdriver
from duxiu.items import DuxiuItem


class DuxiuSpiderSpider(scrapy.Spider):
    name = 'duxiu_spider'
    allowed_domains = ['book.duxiu.com']
    start_urls = ['http://book.duxiu.com/book.do?go=guideindex']
    browser = webdriver.Chrome()
    category_num = -1
    subtype_num = -1
    cur_category = 1
    cur_subtype = 0
    # mm = 0

    def start_requests(self):
        yield scrapy.Request("http://www.duxiu.com/", callback=self.enter_website, dont_filter=True)

    def enter_website(self, response):
        self.browser.get('http://www.duxiu.com/')
        time.sleep(1)
        self.browser.find_element_by_xpath("//li//a[@class='leftF']").click()
        self.browser.get(''.join(self.start_urls))
        self.category_num = len(self.browser.find_elements_by_xpath("//ul[@class='tba_list']//li"))
        yield scrapy.Request(''.join(self.start_urls),  callback=self.next_enter, dont_filter=True)

    def next_enter(self, response):
        self.browser.get('http://book.duxiu.com/book.do?go=guideindex')
        # Judge whether to change or not
        if self.subtype_num == self.cur_subtype:
            self.cur_category = self.cur_category + 1
            self.cur_subtype = 0

        self.cur_subtype = self.cur_subtype + 1

        # Parse current number of subtype
        if self.cur_subtype == 1:
            xpath = "//div[@class='typesub'][" + str(self.cur_category) + "]//li"
            self.subtype_num = len(self.browser.find_elements_by_xpath(xpath))

        # Parse next URL of subtype
        xpath = "//div[@class='typesub'][" + str(self.cur_category) + "]//li[" + str(self.cur_subtype) + "]/a"

        self.start_urls = self.browser.find_element_by_xpath(xpath).get_attribute('href')
        yield scrapy.Request(''.join(self.start_urls), callback=self.parse, dont_filter=True)

    def parse(self, response):
        self.browser.get(''.join(self.start_urls))
        # if self.mm == 0:    # Test
        #     self.browser.get("http://book.duxiu.com/book.do?go=guidesearch&flid=1533&isort=0&pages=8")
        #     self.mm = self.mm + 1
        time.sleep(1)
        book_list = self.browser.find_elements_by_xpath("//ul[@class='clearfix']//li")

        for i_item in book_list:
            # Save to Item
            duxiuItem = DuxiuItem()
            duxiuItem['category'] = self.browser.find_element_by_xpath("//li[@class='tba_cont']/a").text
            duxiuItem['subtype'] = self.browser.find_element_by_xpath("//ul[@class='tba_list']//ul//a[@class='current']").text
            duxiuItem['title'] = i_item.find_element_by_xpath(".//dt/a").text
            duxiuItem['author'] = i_item.find_element_by_xpath(".//dl/dd[1]").text
            duxiuItem['date_of_pub'] = i_item.find_element_by_xpath(".//dl/dd[2]").text
            duxiuItem['pages'] = i_item.find_element_by_xpath(".//dl/dd[3]").text
            duxiuItem['url'] = i_item.find_element_by_xpath(".//dt/a").get_attribute("href")
            print(duxiuItem)
            yield duxiuItem

        try:
            next_link = self.browser.find_element_by_link_text("下一页").get_attribute('href')
        except:
            next_link = None
        if next_link :
            self.start_urls = next_link
            yield scrapy.Request(next_link, callback=self.parse, dont_filter=True)
        elif self.category_num > self.cur_category:
            self.start_urls = ['http://book.duxiu.com/book.do?go=guideindex']
            yield scrapy.Request(''.join(self.start_urls), callback=self.next_enter, dont_filter=True)