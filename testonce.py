import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv

# 配置
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
BASE_URL = 'https://www.tripadvisor.com'
COUNTRY_URL = f'{BASE_URL}/Attractions-g293915-Activities-China.html'

# 初始化CSV
with open('tripadvisor_attractions.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['景点名称', '地址', '营业时间', '评论'])


def get_attraction_links():
    """获取景点详情页链接"""
    response = requests.get(COUNTRY_URL, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = []
    for item in soup.select('div.listing_title a'):
        if len(links) >= 100:
            break
        links.append(BASE_URL + item['href'])
    return links


def get_attraction_detail(url):
    """使用Selenium处理动态加载的营业时间和评论"""
    driver = webdriver.Chrome()
    driver.get(url)
    data = {}

    try:
        # 获取地址
        data['name'] = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'h1'))
        ).text
        data['address'] = driver.find_element(By.CSS_SELECTOR, 'div.dgUjX').text

        # 展开营业时间
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.HsCAs'))
        ).click()
        data['hours'] = driver.find_element(By.CSS_SELECTOR, 'div.cxCVT').text

        # 加载评论
        reviews = []
        for _ in range(2):  # 假设每页5条评论，加载2页
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.YibKl'))
            )
            page_reviews = [r.text for r in driver.find_elements(By.CSS_SELECTOR, 'q.XllAv')][:10 - len(reviews)]
            reviews.extend(page_reviews)
            if len(reviews) >= 10:
                break
            driver.find_element(By.CSS_SELECTOR, 'a.nav.next').click()
            time.sleep(2)
        data['reviews'] = reviews[:10]

    finally:
        driver.quit()

    return data


# 主程序
attraction_links = get_attraction_links()
for link in attraction_links[:5]:  # 示例仅爬取前5个
    detail = get_attraction_detail(link)
    with open('tripadvisor_attractions.csv', 'a', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            detail.get('name', ''),
            detail.get('address', ''),
            detail.get('hours', ''),
            ' | '.join(detail.get('reviews', []))
        ])
    time.sleep(5)  # 降低请求频率