# 笔趣看小说下载

# 目标：1.搜索小说 2.查看章节 3.下载章节内容

# 1.输入小说名称：发起请求,获取小说的列表
def welcome_biqukan():
    print('*************欢迎笔趣看助手*************')
    # 1.1 创建输入框
    book_name = input('请输入你要搜索的小说名称: ')
    print(book_name)
    get_book_list(book_name) # 调用获取boot_list函数

def get_book_list(book_name):
    # 1.2 准备url和提交参数
    url = 'https://www.2biqukan.com/novel/search'
    # 1.3 参数 s1:0 按小说名字搜索 2.keyword：bookname 3._csrf:认证
    params = {'s1':'0','keyword':book_name,'_csrf':'UVBsbkRXY2I4HhxefBgSWmghGwYMejEHZjszWXM1NAAnFwU7MxsqKw%3D%3D'}
    # 1.4 发起请求
    response = requests.get(url=url,params=params)
    print(response.status_code,response.url)
    # 1.5 判断是否访问成功
    if response.status_code == 200:
        html = response.text
        # 1.6 解析网页源代码
        soup = BeautifulSoup(html,'html5lib')
        li_list = soup.find_all(name='li',attrs={'class':'col-md-6 col-xs-12'})
        print(li_list)
        # 1.7 遍历小说列表
        for li in li_list:
            book_name = li.a.string
            book_author = li.find(name='a',attrs={'class':'s-author'}).string
            book_url = li.a.attrs['href']
            print('小说名称:'+book_name+'\t'+
                  '作者:'+book_author+'\t'+
                  '地址:'+book_url)
    else:
        print('你输入有误，不存在')
        welcome_biqukan()

# 2.输入小说，获取章节列表
def get_book_chapter_list():
    pass
# 3.根据章节列表，实现本地存储
def get_book_chapter_list_content():
    pass

# 入口
if __name__ == '__main__':
    import requests
    from bs4 import BeautifulSoup
    welcome_biqukan()









