# -!- coding: utf-8 -!-
import requests
from lxml import etree
import json
import pymysql
import re
import threading
import os

json_url = 'https://car.autohome.com.cn/duibi/ashx/specComparehandler.ashx?&type=1&seriesid={}'
config_url = 'https://car.autohome.com.cn/config/series/{}.html'
sid_url_config0 = 'https://carif.api.autohome.com.cn/Car/Spec_ParamListBySpecList.ashx?_callback=paramCallback&speclist={}'
sid_url_config1 = 'https://carif.api.autohome.com.cn/Car/Config_ListBySpecIdList.ashx?_callback=configCallback&speclist={}'
url = 'https://www.autohome.com.cn/grade/carhtml/{}.html' #以之母分的汽车页面

def get_url(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36',
               }
    response = requests.get(url,headers=headers)
    html_str = response.text
    return html_str

def car_name(html_str):   #车型名字
    html = etree.HTML(html_str)
    car_name_html = html.xpath('//div[@class="subnav-title-name"]')
    ret = car_name_html[0].xpath('string(.)').strip()
    return ret

def save_jpg(jpg_url,jpg_name):
    dir = 'Logo'
    if not os.path.isdir(dir):
        os.makedirs(dir)
    jpg_name = jpg_name+'.jpg'
    file_name = os.path.join(dir,jpg_name)
    jpg = requests.get(jpg_url)
    with open(file_name,'wb') as f:
        f.write(jpg.content)
    file_name = 'Logo/'+jpg_name
    return file_name




def get_content_list(html_str):  #取在售车的id号列表
    car_dict = {}
    html = etree.HTML(html_str)
    html_int_id = html.xpath('//dl/@id')
    car_brands_num_list = []
    for i in html_int_id:
        car_brands = html.xpath('//dl[@id="{}"]//div/a[@class="red"]/@href'.format(i))
        car_logo = html.xpath('//dl[@id="{}"]/dt/a/img/@src'.format(i))
        car_logo_name = html.xpath('//dl[@id="{}"]/dt/div/a/text()'.format(i))
        ll = []
        for n in car_logo:
            ll.append('http:'+n)
        for n in car_logo_name:
            ll.append(n)
        if car_brands:
            car_brands = list(set(car_brands))
            car_brands_list = []
            for num in car_brands:
                num = num.split('/')[3]
                print(num)
                car_brands_list.append(num)
        try:
            car_dict[tuple(car_brands_list)] = ll
        except Exception:
            continue


    return car_dict

def sell_car_brands(json_url):   ##在售车的sid号码

    car_sid_list = []
    text = get_url(json_url)
    text = json.loads(text)
    try:
        l = text['List'][0]['List']
    except Exception:
        return None
    for i in l:
        car_sid_list.append(i['I'])

    return car_sid_list

def save_mysql(leter,name,text,jpg_path):  ##保存到数据库

    car_config1 = []
    host = "10.0.0.120"
    db_user = "qq"
    db_password = "123456"
    database = "che"
    conn = pymysql.connect(host=host,user=db_user,password=db_password,database=database,charset='utf8')
    cursor = conn.cursor()
    name1 = name.rsplit('-', 1)
    name2 = name1[0]
    car_name1 = text["车型名称"]
    car_config1.append(str(text).replace("'",'"'))
    car_config1 = str(car_config1).replace("'",'')
    sql = "insert into che_get_api(ga_letter,ga_brand_name,ga_typename,ga_car_name,ga_fileurl,ga_config) values(%s,%s,%s,%s,%s,%s)"
    rows = cursor.execute(sql,(leter,name2,name,car_name1,jpg_path,car_config1))
    conn.commit()
    cursor.close()
    conn.close()


def save_json_text(name,text,L):  ##保存为json文件

    HOME_DIR = '汽车之家'
    if not os.path.isdir(HOME_DIR):
        os.makedirs(HOME_DIR)
    leter_dir = os.path.join(HOME_DIR,L)
    if not os.path.isdir(leter_dir):
        os.makedirs(leter_dir)
    name1 = name.rsplit('-',1)
    name2 = name1[0]
    name_dir = os.path.join(leter_dir,name2)
    if not os.path.isdir(name_dir):
        os.makedirs(name_dir)
    name = os.path.join(name_dir,name)
    with open(name + '.json', 'a',encoding='utf-8') as f:
        f.write(text)
        f.write('\n')


def car_config(sid):   ##获取配置信息)

    config_dict = {}
    html = get_url(sid_url_config0.format(sid))
    html1 = get_url(sid_url_config1.format(sid))
    car_dict1 = re.findall('{.*}', html)
    x1 = eval(car_dict1[0])
    for num in range(6):
        l1 = x1['result']['paramtypeitems'][num]['paramitems']
        for j in l1:
            config_dict[j['name']] = j['valueitems'][0]['value']
            # config_dict.append(s)
    car_dict2 = re.findall('{.*}', html1)
    x2 = json.loads(car_dict2[0])
    l2 = x2['result']['configtypeitems']
    for i in l2:
        for v in i['configitems']:
            v['valueitems'][0]['value'] = str(v['valueitems'][0]['value']).replace('&nbsp;','')
            config_dict[v['name']] = v['valueitems'][0]['value']

    return config_dict

def run(leter_url,l):
    L = l
    car_dict = get_content_list(get_url(leter_url))
    for key,value in car_dict.items():
        jpg_url = value[0]
        jpg_name = value[1]
        jpg_path = save_jpg(jpg_url,jpg_name)
        for i in key:
            html = get_url(config_url.format(i))
            name = car_name(html)
            try:
                json_text = sell_car_brands(json_url.format(i))
                for i in json_text:
                    i = car_config(i)
                    print(i)
                    save_mysql(L,name,i,jpg_path)

            except Exception:
                continue


if __name__ == '__main__':
    leter_list = []
    for i in range(65,91):
        i = chr(i)
        l = i
        if i == 'U':
            continue
        run(url.format(i),i)
