import requests
import pymongo
from requests import RequestException
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from multiprocessing import Pool
from chardet import detect

slide_title = ''
slide_article = ''


def get_page_yule():
    # 获取当前页面所有包含新闻a的标签
    news = browser.find_elements_by_xpath('//div[@class="d_list_txt"]/ul/li/span/a')
    # 进程池
    p = Pool(4)
    for i in news:
        link = i.get_attribute('href')  # 得到新闻的url
        print('滚动网页阶段：', link, i.text)
        # 一般网页：
        if not news_col.find_one({'link': link}) and link.find('://ent', 0, len(link)) != -1:
            print('多进程爬取ent娱乐内容：')
            p.apply_async(get_ent_txt(link))
        # slide网页：
        elif not news_col.find_one({'link': link}) and link.find('://slide.ent', 0, len(link)) != -1:
            print('多进程爬取slide娱乐内容：')
            p.apply_async(get_slide_txt(link, i.text, i.text))
        # video网页：
        elif not news_col.find_one({'link': link}) and link.find('://video', 0, len(link)) != -1:
            print('多进程爬取video娱乐内容：')
            p.apply_async(get_video_txt(link))
        else:
            pass
    p.close()
    p.join()


def get_ent_txt(link):  # 获取每条新闻的详细内容
    html = get_response(link)
    if html:
        # 使用beautifulsoup进行解析
        soup = BeautifulSoup(html, 'lxml')

        # 标题
        title = soup.select('.main-title')
        if not title:
            title = soup.select('#artibodyTitle')
        if title:
            title = title[0].text
        print('文章标题：', title)

        # 内容
        article = soup.select('div[class="article"] p')
        if not article:
            article = soup.select('div[id="artibody"] p')
        # if not article:
        #    article = soup.select()
        if article:
            article_list = []
            for i in article:
                print('文章内容：', i.text)
                article_list.append(i.text)

        if article and title:
            # 每一条新闻 都转为字典格式
            news = {'link': link, 'title': title, 'article': article_list}
            news_col.insert_one(news)
            print('已存储至mongodb中')


def get_slide_txt(link, slide_title, slide_article):  # 爬取slide网页的文本
    """
    html = get_response_slide(link)
    # 使用beautifulsoup进行解析
    soup = BeautifulSoup(html, 'lxml')
    """
    title = slide_title
    article = slide_article
    print('文章标题：', title)
    print('文章内容', article)
    if title and article:
        # 每一条新闻 都转为字典格式
        news = {'link': link, 'title': title, 'article': article}
        news_col.insert_one(news)
        print('已存储至mongodb中')
    """
    # 标题 从打开的网页再提取一遍
    title = soup.select('head title')
    # if not title:
    #   title = soup.select('#artibodyTitle')
    if title:
        title = title[0]
        print('文章标题：', title.content)
        print('编码方式：', detect(title.content))

    # 内容
    article = soup.select('meta[name="description"]')[0]
    print('编码方式', detect(article))
    if article:
        article_list = []  # 存储所有的文本段
        print('文章内容：', type(article.content))
        article_list.append(article.content)
        '''
        article_list = []  # 存储所有的文本段
        for i in article:
            print('文章内容：', i.text)
            article_list.append(i.text)
        '''
"""


def get_video_txt(link):  # 爬取video网页的文本
    html = get_response(link)
    # 使用beautifulsoup进行解析
    if html:
        soup = BeautifulSoup(html, 'lxml')

        # 标题
        title = soup.select('div[class="Vd_titBox clearfix"] h2')
        if not title:
            title = soup.select('div[class="Vd_titBox clearfix"]')
        if title:
            title = title[0].text
        print('文章标题：', title)

        # 内容
        article = soup.select('em[task="oldinfor"] p')
        if not article:
            article = soup.select('em[task="oldinfor"]')
        if article:  # article爬出来是一个节点list，里面有文本
            article_list = []  # 存储所有的文本段
            for i in article:
                print('文章内容：', i.text)
                article_list.append(i.text)
        if article:
            # 每一条新闻 都转为字典格式
            news = {'link': link, 'title': title, 'article': article_list}
            news_col.insert_one(news)
            print('已存储至mongodb中')


def get_response(url):  # 每条新闻点进去之后并不是动态页面 使用requests进行爬取
    try:
        # 添加user-Agent，放在headers中，伪装成浏览器
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            response.encoding = 'utf-8'
            return response.text
        return None
    except RequestException:
        return None


def get_response_slide(url):  # 每条新闻点进去之后并不是动态页面 使用requests进行爬取
    try:
        # 添加user-Agent，放在headers中，伪装成浏览器
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            response.encoding = 'utf-8'
            return response.text
        return None
    except RequestException:
        return None


if __name__ == '__main__':
    # 连接mongodb
    client = pymongo.MongoClient('mongodb://localhost:27017')
    # 指定数据库
    db = client.CaiJing
    # 指定集合
    news_col = db.sinaRollEnt
    # 打开浏览器
    browser = webdriver.Chrome()
    browser.implicitly_wait(10)
    # 打开网址
    browser.get('http://ent.sina.com.cn/rollnews.shtml#pageid=382&lid=2990&k=&num=50&page=950')
    # 获取当前页面新闻的url
    get_page_yule()
    while True:
        try:
            # 找到下一页的按钮 并点击
            print('爬取：')
            browser.find_element_by_xpath('//a[@onclick="newsList.page.next();return false;"]').click()
            get_page_yule()
        except NoSuchElementException:
            print("No Such Element Exception")
            browser.close()
            break
