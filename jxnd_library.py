import requests
import json
import random
import urllib
from lxml import etree
import time
import threading


"""江西农业大学图书馆图书信息爬虫
目标：按目录分类获取各级目录下的图书信息，即将图书信息分类保存
总体分析
1)获取该级目录下的图书，需要获取该级目录nodeId(id)，callName(name中的一部分)，callNumber(name中的一部分)等信息
2)而要获取该级目录的一些信息，必须获取上级目录的id(id), name(n), pId(lv)才能构建url来获取该级目录信息
（因为该网站所有图书目录均为异步加载(要想获取异步加载的内容只有两种办法，一种是用自动化工具；另一种就是构建目标url)，
所以必须要构建你要获取信息的url)
3)获取第一级目录信息，用以构建url获取第二级目录信息
4)获取第二级目录信息后，构建该级目录下获取图书信息的url，并获取图书信息保存，完成任务
"""

# eval函数中不能包含null,true,false字符串，用全局变量去替换字符串中的这些字符
globals = {
    'true': 1,
    'false': 0,
    '/': ' '
}

def loadUserAgents(uafile):
    uaList = []
    with open(uafile, 'r') as uaf:
        for ua in uaf.readlines():
            uaList.append(ua.strip()[1: -1])
    uaf.close()
    random.shuffle(uaList)
    return uaList
userAgentFile = r"C:\Users\zwh\Desktop\user_agents.txt"
uaList = loadUserAgents(userAgentFile)

def loadProxies(pfile):
    proxies_list = []
    with open(pfile, 'r') as pf:
        for proxies in pf.readlines():
            proxies_list.append(proxies)
    pf.close()
    return proxies_list
proxiesFile = r"C:\Users\zwh\Desktop\proxies.txt"
proxies_list = loadProxies(proxiesFile)

# 获取第一级图书目录信息（id(节点的排列顺序), pId(所在目录等级，即为第几级目录), name(目录名称),
# isParent(判断是否为父目录，即其下是否有子目录))
def parser1(url):
    res = requests.get(url)
    if res.status_code == 200:
        for dict in eval(res.text, globals):
            try:
                # print(dict['id'], dict['pId'], dict['name'].replace('<B>', '').replace('</B>', ''), dict['isParent'])
                id = dict['id']
                pId = dict['pId']
                name = dict['name'].replace('<B>', '').replace('</B>', '')
                isParent = dict['isParent']
                parser2(id, pId, name, isParent)
            except Exception as e:
                print(e)

# 获取详细的图书目录信息(需要第一级图书目录信息中的id，name，pId以及isParent用于判断其下是否包含子目录，
# 如果包含则继续获取子目录)
def parser2(id, pId, name, isParent):
    base_url = "http://219.229.222.149:8080/opac/getClassNumberTree?"
    params = {'id': id,
              'n': name,
              'lv': pId,
              'otherParam': 'zTreeAsyncTest',
              '_': '153439533{}'.format(random.randint(7000, 9000))}
    if isParent:
        url = base_url + urllib.parse.urlencode(params)
        res = requests.get(url)
        for dict in eval(res.text, globals):
            try:
                id = dict['id']
                pId = dict['pId']
                name = dict['name']
                isParent = dict['isParent']
                if isParent:
                    parser2(id, pId, name, isParent)
                dictory_list.append(dict)
                # print(dict)
            except Exception as e:
                print(e)

# 根据根据详细的图书目录信息，构建将要抓取的书库url，并且抓取其中的图书总数，由此得出将要抓取网页的页数（page），
# 然后抓取图书信息（序号、题名、责任者、出版信息、索书号、馆藏\可外借),并按图书类别保存到本地
def parser3(dict):
    path = "C:\\Users\\zwh\\Desktop\\python实例\\python爬虫\\jxnd_library\\" + dict['name'].replace('/', ' ') + ".txt"
    f = open(path, 'a')
    with sem:
        print(threading.current_thread().name)
        base_url = "http://219.229.222.149:8080/opac/browseByCategory?"
        for i in range(1000):  # 先设置一个较大的数，在下面获取得知页数，并且结束
            local.i = i
            try:
                headers = {"User-Agent": random.choice(uaList)}
                params = {
                    'callNumber': dict['name'].split()[0],
                    'callName': dict['name'].split()[1],
                    'type': '',
                    'typename': '请选择校区 / 分馆',
                    'libraryId': '',
                    'libraryName': '所有校区',
                    'sort': 'latestEntryDate',
                    'nodeId': dict['id'],
                    'pager.offset': 25*i}
                url = base_url + urllib.parse.urlencode(params)
                res = requests.get(url, headers=headers)
                # time.sleep(random.randint(1,2))
                # 一、请求头不好用，有可能会造成请求失败
                # 二、由于在网上抓取的代理不稳定，可以先用自己的ip抓取，如果被封则用代理
                for i in range(3):
                    if res.status_code != 200:
                        print("请求头错误，更换请求头重新请求")
                        headers = {"User-Agent": random.choice(uaList)}
                        proxies = eval(random.choice(proxies_list))
                        res = requests.get(url, headers=headers, proxies=proxies, timeout=30)
                    else:
                        break
                        # return
                if res.status_code == 200:
                    tree = etree.HTML(res.text)
                    books = tree.xpath("//table[@class='jp-booksList']/tbody//tr")
                    for book in books:
                        try:
                            num = book.xpath("./td[@class='text-center']/text()")[0].strip()
                            name = book.xpath("./td[4]/a/text()")[0].strip()
                            bookHref = "http://219.229.222.149:8080" + book.xpath("./td[4]/a/@href")[0].strip()
                            compiler = book.xpath("./td[5]/text()")[0].strip()
                            publishers = book.xpath("./td[6]/text()")[0].strip()
                            callNumber = book.xpath("./td[7]/text()")[0].strip()
                            holding = book.xpath("./td[8]/text()")[0].strip()

                            tblt = "{0:^5}\t{1:{6}^40}\t{2:{6}^40}\t{3:{6}^10}\t{4:^10}\t{5:^10}\n"
                            f.write(tblt.format(num, name, compiler, publishers, callNumber, holding,chr(12288)))
                            print(num, name, bookHref, compiler, publishers, callNumber, holding)
                        except Exception as e:
                            print(e)

                # 获取该分类下共有多少条记录，用于计算页数，并结束循环
                allNums = tree.xpath("//font[@class='red']/text()")[0].strip()
                print(allNums)
                pages = int(allNums) // 25 + 1
                if (local.i + 1) >= pages:
                    break

            except Exception as e:
                print(e)
        f.close()

# TODO 存储到MongoDB,redis数据库中

if __name__ == "__main__":
    time1 = time.time()
    dictory_list = []   # 目录总数为226
    start_url = "http://219.229.222.149:8080/opac/getClassNumberTree?id=1&n=+%E4%B8%AD%E5%9B%BE%E5%88%86%E7%B1%BB&lv=0&otherParam=zTreeAsyncTest&_=1534395336898"
    parser1(start_url)

    # 创建线程
    local = threading.local()
    thread_list = []
    sem = threading.Semaphore(5)
    for dict in dictory_list:
        print(dict)

        t = threading.Thread(target=parser3, args=(dict, ))
        thread_list.append(t)
        t.start()

    for t in thread_list:
        t.join()

    time2 = time.time()
    print("总耗时：%d" % (time2 - time1))







