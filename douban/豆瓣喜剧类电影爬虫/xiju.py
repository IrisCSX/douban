import requests
from lxml import html


__author__ = 'gua'


# 这个类很奇怪
# 其实是用来让电影能够自行打印出所有属性的值的一个东西
# 忽略掉
class Model(object):
    # 自动化打印对象
    def __repr__(self):
        class_name = self.__class__.__name__
        properties = ('{} = ({})'.format(k, v) for k, v in self.__dict__.items())
        return '\n<{}:\n  {}\n>'.format(class_name, '\n  '.join(properties))


# 这是一个电影类（用来存储信息的）
class Movie(Model):
    def __init__(self):
        # 电影类有 4 个属性
        self.name = ''  # 电影名字
        self.score = 0  # 豆瓣得分
        self.cover_url = '' # 图片链接
        self.reviews = 0    # 评价人数

# 从一个div里面得到一个movie实例
def movie_from_div(div):
    movie = Movie()
    # 这个和之前的 xpath 是一样的语法
    # 不同的是 .// 表示在当前节点内查找，即只在这个div里面找数据，不在其它地方找
    # 因为返回的是一个 list (哪怕只有一个元素)
    # 所以要 [0] 取到第一个节点
    # 再通过 .text 获取到文本信息<span class="title">肖申克的救赎</span>，即中间的文本
    # <span class="title"
    movie.name = div.xpath('.//a[@class=""]')[0].text[:-1].strip('/').strip()
    print(movie.name)
    movie.score = div.xpath('.//span[@class="rating_nums"]')[0].text
    # movie.reviews = div.xpath('.//div[@class ="star"]/span')[-1].text[:-3]
    movie.reviews = div.xpath('.//span[@class ="pl"]')[0].text[:-4][1:]
    # print(movie.reviews)
    # print(movie.name, movie.reviews)
    img_url = div.xpath('.//img/@src')[0]  # @符号是取属性的
    # print(img_url)
    movie.cover_url = img_url
    return movie


# 缓存爬虫页面（把爬虫的页面下载下来）
def cached_url(url):
    import os
    filename = url.split('=')[-1] + '.html'
    path = os.path.join('xiju_cached', filename)  # 得到cached/0.html
    if os.path.exists(path): # 爬过的页面直接文件读取
        with open(path, 'rb') as f:
            return f.read()
    else: # 没爬过的页面，下载下来
        r = requests.get(url) # 得到链接的响应
        with open(path, 'wb') as f:  # 以二进制文件读取，用with是保护操作系统的操作文件后正确关闭文件
            f.write(r.content)
        return r.content


# 得到URL中的所有实例
def movies_from_url(url):
    page = cached_url(url)
    root = html.fromstring(page)
    movie_divs = root.xpath('//table[@class=""]')
    movies = [movie_from_div(div) for div in movie_divs]
    return movies


def download_img(url, name):
    r = requests.get(url)   # 用get请求的到URL的响应，而它是一个图片，所以得到的响应不是原始信息，它的content才是原始信息
    # 通过 URL 获取到图片的数据并且写入文件
    # 'wb' 表明是 写入(write) 和 二进制(binary)，因为图片是二进制的
    path = 'covers/' + name
    with open(path, 'wb') as f:
        f.write(r.content)


# 保存每一个电影的图片
def save_covers(movies):
    for m in movies:
        download_img(m.cover_url, m.name + '.jpg')


def main():
    for i in range(0, 100, 20):   # 加上for 循环就能取出全部，找每页的url规律
        url = 'https://movie.douban.com/tag/%E5%96%9C%E5%89%A7?start={}'.format(i)
        movies = movies_from_url(url)
        print(movies)
        # save_covers(movies)


if __name__ == '__main__':
    main()
