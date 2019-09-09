def get_html():
    response = requests.get(url=URL)
    print('状态码：',response.status_code)
    if response.status_code == 200:
        response.encoding = 'utf-8'
        html = response.text
        # print(html)
        return html
    else:
        print('请求失败')


def parser_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.title.string
    print(soup.title.string)

    import re
    title = re.sub('[\n]+','',title)

    file = open(title + '.txt', 'w', encoding='utf-8')
    div_list = soup.find(name='ol', attrs={'class': 'grid_view'})

    div_li = div_list.find_all(name='li')
    # print(len(div_li))

    for div in div_li:
        top = div.find(name='em').string
        name = div.find(name='span', attrs={'class': 'title'}).string
        # # 2.6 获取标签的属性: tag.attrs
        numbers = div.find(name='span', attrs={'class': 'rating_num'}).string
        img = div.find(name='img').attrs['src']
        
        if 'http' not in img:
            img = 'https://movie.douban.com/top250' + img
        print(top, name, numbers, img)

        save_douban_info(file, top, name, numbers, img)  # 存储
        img_dict[name] = img

    file.flush()  # 清缓存
    file.close()  # 关闭

def save_douban_info(file, top, name, numbers, img):
    file.write(top + '\t' + name + '\t' + numbers + '\t' + img + '\n')
#
def download():
    # 4.1 创建目录
    downloadpath = 'top25电影库'
    # 4.2 判断目录是否存在
    if not os.path.exists(downloadpath):
        # 4.3 创建
        os.mkdir(downloadpath)

    for key in img_dict.keys():
        # 捕捉异常
        try:
           # 下载 1.下载路径 2.存储路径
           urlretrieve(img_dict[key],downloadpath+'/'+key+'.jpg')
           print(key, '下载成功~~~~~')
        except:
            print(key,'下载失败~~~~~')



if __name__ == '__main__':
    import requests
    from bs4 import BeautifulSoup
    import os # 负责目录的创建、修改、删除
    from urllib.request import urlretrieve # 下载网络资源

    # 图片字典：img_dict name:img
    img_dict = {}
    # 爬取地址
    URL = 'https://movie.douban.com/top250'
    # 定制头部
    HEAD = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36"}

    html = get_html() # 调用一：发起请求，返回源代码
    parser_html(html) # 调用二：解析、抽取数据
    download() # 调用四：下载图片