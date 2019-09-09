import csv
import os

import requests
from lxml import etree


# 构造请求对象
def create_requests(url, page, fl):
    fl_url = url % (fl, page)
    # print(fl_url)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}

    return requests.get(url=fl_url, headers=headers)


# 发起请求
def requests_data(req):
    return req.content.decode('utf-8')


# 解析页面
def anylasis_html(html):
    # 用etree把整个html字符串加载出来，生成一棵节点树
    html_tree = etree.HTML(html)
    # 获取整页所有图书列表
    book_list = html_tree.xpath("//div[@class='content']//li")

    for book in book_list:
        item = {}
        # 标题b
        item['title'] = book.xpath(".//div/a/span/text()")[0]
        item['name'] = book.xpath(".//div/a/text()")[0]
        item['url'] = 'https://www.ximalaya.com/' + book.xpath(".//div/div/a/@href")[0]
        yield item


def write_to_txt(data, fl):
    # 在写csv的时候，首先需要把data整合成一个二维列表
    # 定义一个大列表，用于存储所有的有声书信息
    txt_items = []
    for books in data:
        for book in books:
            # book是字典，按照键值的形式存储了每个有声书的信息，取出值，写入一个列表
            item = []
            # 遍历book字典依次去除每一个值
            for k, v in book.items():
                item.append(v)
            txt_items.append(item)
    # 写入csv
    # file_name = './file/%s.txt' % fl
    file_path = os.getcwd() + r'\file'
    if not os.path.exists(file_path):
        os.mkdir(file_path)
    file_name = file_path + (r'\%s.txt' % fl)
    with open(file_name, 'w', encoding='utf-8') as fp:
        # 用fp来创建一个csv的写对象
        w = csv.writer(fp)
        # 写表头
        w.writerow(["title", "name", "url"])
        # 写数据
        w.writerows(txt_items)


# 获取分类信息
def get_classification(initial_url, headers):
    req = requests.get(url=initial_url, headers=headers)
    # print(req.status_code)
    html = req.content.decode('utf-8')
    html_tree = etree.HTML(html)

    classification_list = html_tree.xpath("//div[@class='category-filter-body']/div[1]/div[1]/a/@data-code")
    # print(classification_list)
    return classification_list


def main():
    initial_url = 'https://www.ximalaya.com/youshengshu/'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}

    url = 'https://www.ximalaya.com/youshengshu/%s/p%d/'

    classification_list = get_classification(initial_url, headers)
    # print(classification_list)
    for fl in classification_list:
        book_list = []
        for page in range(1, 35):
            # 构造请求对象
            req = create_requests(url, page, fl)
            # 发起请求
            html = requests_data(req)
            # 解析数据
            res = anylasis_html(html)
            book_list.append(res)

        # 存储数据 txt
        write_to_txt(book_list, fl)
        print("下载%s完成" % fl)


if __name__ == '__main__':
    main()
