
from spider.lagou import LagouSpider


if __name__ == '__main__':
    lagou = LagouSpider(keyword="大数据",
                        login_username="18666270636",
                        login_password="379978424")
    res = lagou.parse()
    print(res)

