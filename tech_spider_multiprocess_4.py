import requests
import pymongo
from requests import RequestException
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from multiprocessing import Pool


def get_page_tech():
    # 获取当前页面所有包含新闻a的标签
    news = browser.find_elements_by_xpath('//div[@class="d_list_txt"]/ul/li/span/a')
    # 进程池
    p = Pool(4)
    for i in news:
        link = i.get_attribute('href')  # 得到新闻的url
        print('滚动网页阶段：', link, i.text)
        if not news_col.find_one({'link': link}) and link.find('http://video', 0, len(link)) == -1:  # 如果是视频网页就跳过
            print('多进程爬取科技内容：')
            p.apply_async(get_tech(link))
            print('【爬取完毕')
    p.close()
    p.join()


def get_tech(link):  # 获取每条新闻的详细内容
    print('get_tech执行')
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
        if article:
            article_list = []
            for i in article:
                print('文章内容：', i.text)
                article_list.append(i.text)

        if title and article:
            # 每一条新闻 都转为字典格式
            news = {'link': link, 'title': title, 'article': article_list}
            news_col.insert_one(news)


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


if __name__ == '__main__':
    # 连接mongodb
    client = pymongo.MongoClient('mongodb://localhost:27017')
    # 指定数据库
    db = client.CaiJing
    # 指定集合
    news_col = db.sinaRollTech
    # 打开浏览器
    browser = webdriver.Chrome()
    browser.implicitly_wait(10)
    # 打开网址
    browser.get('https://tech.sina.com.cn/roll/rollnews.shtml#pageid=372&lid=2431&k=&num=50&page=1')
    # 获取当前页面新闻的url
    get_page_tech()
    while True:
        try:
            # 找到下一页的按钮 并点击
            print('爬取：')
            browser.find_element_by_xpath('//a[@onclick="newsList.page.next();return false;"]').click()
            get_page_tech()
        except NoSuchElementException:
            print("No Such Element Exception")
            browser.close()

