
import requests
from lxml import etree
import os


url = 'https://www.biqugesk.org/biquge/150554/' #下载书的地址
BOOK_DIR = '/bookdir'    #保存的目录地址

def get_url(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36',
               }
    response = requests.get(url,headers=headers)
    html_str = response.text
    return html_str

def save_txt(bookname,text):
    if not os.path.isdir(BOOK_DIR):
        os.makedirs(BOOK_DIR)
    name = os.path.join(BOOK_DIR,bookname)
    with open(name + '.txt', 'a', encoding='utf-8') as f:
        f.write(text)
        f.write('\n')

def get_chapter(html_str):
    html = etree.HTML(html_str)
    title_name = html.xpath('//div[@id="info"]/h1/text()')
    bookname = title_name[0].strip().encode('ISO-8859-1').decode('UTF-8')
    href_url = html.xpath('//div[@id="list"]/dl//dd/a/@href')
    return bookname,href_url

def get_text(bookname,html_str):
    html = etree.HTML(html_str)
    chapter = html.xpath('//div[@class="bookname"]/h1/text()')
    text = html.xpath('//div[@id="booktext"]/text()')
    save_txt(bookname,chapter[0].strip().encode('ISO-8859-1').decode('UTF-8'))
    for i in text:
        save_txt(bookname,i.strip().encode('ISO-8859-1').decode('UTF-8'))


if __name__ == '__main__':
    bookname,chapter_url = get_chapter(get_url(url))
    for i in chapter_url:
        get_text(bookname,get_url(i))





