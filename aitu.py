# 1.发起请求、获取网页源代码
def get_html():
    response = requests.get(url)
    # print(response.text)
    print('状态码：', response.status_code)
    if response.status_code == 200:
        response.encoding = 'gb2312'
        html = response.text
        return html
    response.encoding='gb2312'


# 2.构建bs对象，解析、抽取源代码
def parser_html(html):
    soup = BeautifulSoup(html,'html.parser')
    div = soup.find_all(name='div',attrs={'class':'imglist_d'})
    list=div[0].find_all(name='li')
       #print(list)

# 3.创建目录,下载
    downloadpath = '图片库'
    if not os.path.exists(downloadpath):
        os.mkdir(downloadpath)

    for li in list:
        title = li.find(name='div').string
        img_url = li.find(name='img').attrs['src']
        print(title, img_url)
        try:
            urlretrieve(img_url, downloadpath + '/' + title+'.jpg')
            print(title + '下载中..........')
        except:
            print('下载失败........')

# 4.入口
if __name__ == '__main__':
    from bs4 import BeautifulSoup
    import requests
    import os
    from urllib.request import urlretrieve

    url = 'http://www.aiimg.com/photoshop/'
    html = get_html()  # 调用一：发起请求，返回源代码
    parser_html(html)  # 调用二：解析、抽取数据


