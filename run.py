import glob
import os
import re
from collections import OrderedDict
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from crawler import  DynamicPageCrawler
import glob
import os

from bs4 import BeautifulSoup
import re
###函数定义区域
#判断是否已有文件
def file_exists_in_folder(folder_path, file_name):
    for filename in os.listdir(folder_path):
        if filename == file_name:
            return True
    return False
#爬取数据
class MafengwoCrawler:
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    def __init__(self):
        self.data = []
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    def get_page(self, page):
        url = f'http://www.mafengwo.cn/yj/{page}/'
        try:
            resp = self.session.get(url, timeout=10)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            print(f"Error fetching page {page}: {str(e)}")
            return None

    def parse_page(self, html):
        soup = BeautifulSoup(html, 'lxml')
        articles = soup.find_all('div', class_='tn-item')
        for item in articles:
            title = item.find('h2').text.strip()
            author = item.find('a', class_='name').text.strip()
            date = item.find('span', class_='time').text.strip()
            views = re.search(r'\d+', item.find('em').text).group()
            self.data.append({
                'title': title,
                'author': author,
                'date': date,
                'views': int(views)
            })

    def crawl(self, pages=50):
        for page in range(1, pages + 1):
            html = self.get_page(page)
            if html:
                self.parse_page(html)
            time.sleep(1)
        return self.data
def extract_travel_info(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    # 提取标题并清理后缀
    title = soup.title.string.split(' - 马蜂窝')[0].strip()

    # 提取作者信息
    author_meta = soup.find('meta', {'name': 'author'})
    author = author_meta['content'].split(',')[-1].strip() if author_meta else "未知作者"

    # 提取行程基本信息
    travel_info = {
        '出发时间': None,
        '出行天数': None,
        '人均费用': None
    }
    for li in soup.select('.travel_directory ul li'):
        text = li.get_text(strip=True)
        if '出发时间' in text:
            travel_info['出发时间'] = text.split('/')[-1].replace(' ', '')
        elif '出行天数' in text:
            travel_info['出行天数'] = text.split('/')[-1].replace(' ', '')
        elif '人均费用' in text:
            travel_info['人均费用'] = text.split('/')[-1].replace(' ', '')

    # 提取正文前20字（过滤标签）
    content = soup.find('p', class_='_j_note_content')
    first_20_chars = re.sub(r'\s+', '', content.get_text())[:20] + "..." if content else ""

    # 提取行程安排
    itinerary = []
    for h2 in soup.find_all('h2', class_='t9'):
        day_title = h2.get_text(strip=True)
        if 'Day' in day_title:
            itinerary.append(day_title)

    return {
        '标题': title,
        '作者': author,
        **travel_info,
        '行程安排': itinerary,
        '正文摘要': first_20_chars
    }

def find_files_glob(dir_path, ext):
    search_pattern = os.path.join(dir_path, f'*.{ext}')
    files_list = glob.glob(search_pattern)
    return files_list


###读取页面的html
dir_path = '.\\mafengwo_html'
ext = 'txt'
files_list = find_files_glob(dir_path, ext)
id_list=[]
for data_path in files_list:
    # 打开文件
    with open(data_path, 'r', encoding='utf-8') as file:
        # 读取文件内容
        content = file.read()

    # 匹配包含中文的链接模式
    pattern = r'''
        <a\s+                # 开始标签
        href="/i/(24[56]\d+)  # 捕获目标数字
        .*?>                 # 标签属性部分
        (                     # 开始捕获链接文本
            (?:                  
                (?!</a>)         # 否定前瞻确保不跨标签
                [\s\S]           # 匹配任意字符（含换行）
            )*?
            [\u4e00-\u9fa5]     # 必须包含至少一个汉字
            .*?                  
        )                     
        </a>                  # 结束标签
    '''

    # 查找所有匹配项（启用详细模式和跨行匹配）
    matches = re.findall(pattern, content, re.VERBOSE)
    #print(matches)
    # 提取并去重（保留首次出现顺序）
    unique_ids = list(OrderedDict.fromkeys([m[0] for m in matches]))
    for num in range(len(unique_ids)):
        id_list.append(unique_ids[num])
#print(len(id_list),id_list)
i=0
while i<len(id_list):
    url='https://www.mafengwo.cn/i/'+id_list[i]+'.html'
    crawler = DynamicPageCrawler()
    if not file_exists_in_folder('.\\page_html', 'note%d.html'%(i+1)):
        html_content =crawler.get_full_html(url)
        if html_content:
            print("成功获取完整页面内容！",(i+1))
            crawler.save_html(html_content, i+1)
            time.sleep(5)
            i+=1
        else:
            i+=1
    else:
        i+=1




### 分析页面html，数据可视化、保存
dir_path = '.\\page_html'
ext = 'html'
files_list = find_files_glob(dir_path, ext)
result_list=[]
for data_path in files_list:
    html_content = open(data_path, 'r', encoding='utf-8').read()
    result = extract_travel_info(html_content)
    result_list.append(result)

output = '\n'.join(map(str, result_list))
print(output)
# 打开文件，准备写入
with open('note_list.txt', 'w',encoding='utf-8') as file:
    file.writelines(output)
    file.close()


