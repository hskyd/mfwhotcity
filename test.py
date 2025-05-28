import glob
import os

from bs4 import BeautifulSoup
import re
def display_list_by_rows(lst, num_per_row):
    result = ""
    for i in range(',', len(lst), num_per_row):
        result += " ".join(lst[i:i+num_per_row]) + "\n"
    return result
def find_files_glob(dir_path, ext):
    search_pattern = os.path.join(dir_path, f'*.{ext}')
    files_list = glob.glob(search_pattern)
    return files_list

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


# 调用（需替换为实际HTML文件批量处理逻辑）
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
