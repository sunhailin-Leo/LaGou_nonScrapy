# coding:utf-8

# Python内部库
import re
import json
import time
import random
import logging
import requests
from collections import OrderedDict

# 第三方库
from lxml import etree

# 项目内部库
from spider import lagou_login as login
from utils.UserAgentMiddleware import UserAgentRotate


# 日志基本配置
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S')
logger = logging.getLogger()


class LagouSpider:
    def __init__(self, keyword, login_username, login_password):
        """
        拉钩网职位招聘爬虫
        :param keyword: 关键词(默认大数据)
        """
        # 登陆选项
        self._username = login_username
        self._password = login_password

        # 职位名称
        self._keyword = keyword
        if keyword is None:
            self._keyword = "大数据"

        # 请求头
        self._headers = {
            'User-Agent': UserAgentRotate().ua_generator()['User-Agent'],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Referer': 'https://www.lagou.com/jobs/list_%E5%A4%A7%E6%95%B0%E6%8D%AE'
        }

        # 先登陆
        self._login()

        # 初始化登陆cookies
        self.login_cookies = None

        # 全局cookies
        self.all_cookies = {
            'user_trace_token': '20170823200708-9624d434-87fb-11e7-8e7c-5254005c3644',
            'LGUID': '20170823200708-9624dbfd-87fb-11e7-8e7c-5254005c3644 ',
            'index_location_city': '%E5%85%A8%E5%9B%BD',
            'JSESSIONID': 'ABAAABAAAIAACBIB27A20589F52DDD944E69CC53E778FA9',
            'TG-TRACK-CODE': 'index_code',
            'X_HTTP_TOKEN': '5c26ebb801b5138a9e3541efa53d578f',
            'SEARCH_ID': '739dffd93b144c799698d2940c53b6c1',
            '_gat': '1',
            'Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6': '1511162236,1511162245,1511162248,1511166955',
            'Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6': '1511166955',
            '_gid': 'GA1.2.697960479.1511162230',
            '_ga': 'GA1.2.845768630.1503490030',
            'LGSID': '20171120163554-d2b13687-cdcd-11e7-996a-5254005c3644',
            'PRE_UTM': '',
            'PRE_HOST': 'www.baidu.com',
            'PRE_SITE': 'https%3A%2F%2Fwww.baidu.com%2Flink%3Furl%3D7awz0WxWjKxQwJ9xplXysE6LwOiAde1dreMK'
                        'kGLhWzS%26wd%3D%26eqid%3D806a75ed0001a451000000035a128181',
            'PRE_LAND': 'https%3A%2F%2Fwww.lagou.com%2F',
            'LGRID': '20171120163554-d2b13811-cdcd-11e7-996a-5254005c3644'
        }

        # 公司页面的cookies
        self.company_cookies = {
            "user_trace_token": "20171220004039-58e257ca-e4db-11e7-9dd8-5254005c3644",
            "LGUID": "20171220004039-58e25d00-e4db-11e7-9dd8-5254005c3644",
            "X_HTTP_TOKEN": "bcba34cf294f9ac019555f7e20f7425a",
            "showExpriedIndex": "1",
            "showExpriedCompanyHome": "1",
            "showExpriedMyPublish": "1",
            "hasDeliver": "49",
            "gate_login_token": "6f5ec04594af79a97a73cef198de55235579ac1ab9ce660d",
            "TG-TRACK-CODE": "search_code",
            "SEARCH_ID": "94af9f30f25a4466ae245ef64881cf11",
            "index_location_city": "%E5%B9%BF%E5%B7%9E",
            "login": "false",
            "unick": "",
            "_putrc": "",
            "JSESSIONID": "ABAAABAACEBACDGCCD676F349DD3304BDD024C6782CF31D",
            "Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6": "1514991741,1514994780,1516851460",
            "Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6": "1516957761",
            "_gat": "1",
            "LGSID": "20180126170922-992680ba-0278-11e8-9c72-525400f775ce",
            "PRE_UTM": "",
            "PRE_HOST": "",
            "PRE_SITE": "https%3A%2F%2Fwww.lagou.com%2Fjobs%2F4078516.html",
            "PRE_LAND": "https%3A%2F%2Fwww.lagou.com%2Fgongsi%2F140938.html",
            "LGRID": "20180126170922-99268299-0278-11e8-9c72-525400f775ce",
            "_ga": "GA1.2.1566873901.1513701639",
            "_gid": "GA1.2.1326071041.1516851460"
        }

        # 错误列表
        self.err_list = []

    def _login(self):
        # 登陆
        login.login(user=self._username, pass_wd=self._password)
        self.login_cookies = login.get_cookies()
        logger.info(self.login_cookies)

    def parse(self) -> list:
        """
        主要解析的函数
        :return:
        """
        jobs = []
        page_start = 1
        page_end = 31

        # 一共就30页,所以就1-30页, range是1到31
        for page in range(page_start, page_end):
            url = \
                'https://www.lagou.com/jobs/positionAjax.json?px=new&kd=%s&pn=%s&' % \
                (self._keyword, page)
            logger.info(url)
            js_data = requests.get(url=url, headers=self._headers).text
            if '<html>' not in js_data:
                data = json.loads(js_data, object_pairs_hook=OrderedDict)
                logger.debug(dict(data))
                if data['success'] is True:
                    data = data['content']['positionResult']['result']
                    for item in data:
                        try:
                            job = OrderedDict()
                            # 招聘信息页面
                            position_info = self.get_job_info(job_id=item['positionId'],
                                                              cookies=self.all_cookies)
                            # 薪资(最低最高)
                            try:
                                salary = item.get('salary').split('-')
                                job['min_salary'] = salary[0]
                                job['max_salary'] = salary[1]
                            except IndexError:
                                salary = item.get('salary').replace('以上')
                                job['min_salary'] = salary
                                job['max_salary'] = ""
                            # 工作地址
                            try:
                                job['location'] = item['city'] + item['district']
                            except TypeError:
                                job['location'] = item['city']
                            # 发布时间
                            job['publish_date'] = item['createTime']
                            # 职位类型
                            job['work_type'] = item['jobNature']
                            # 工作年限
                            job['work_experience'] = item['workYear']
                            # 教育水平
                            job['limit_degree'] = item['education']
                            # 招聘人数
                            job['people_count'] = 0
                            # 职位名称
                            job['work_name'] = item['positionName']
                            # 工作职责
                            job['work_duty'] = ""
                            # 工作需求
                            job['work_need'] = ""
                            # 工作职责(无法划分..)
                            job['work_content'] = position_info
                            # 职位页面
                            job['work_info_url'] = \
                                "https://www.lagou.com/jobs/%s.html" % item['positionId']
                            # 公司页面请求
                            company_info = \
                                self.get_company_rate(company_id=item['companyId'],
                                                      cookies=self.company_cookies)
                            # 公司名称
                            job['business_name'] = item['companyFullName']
                            # 公司状态
                            job['business_type'] = item['financeStage']
                            # 公司人数规模
                            job['business_count'] = item['companySize']
                            # 公司官网
                            job['business_website'] = company_info[0]
                            # 公司行业类别
                            job['business_industry'] = item['industryField']
                            # 公司地址
                            job['business_location'] = company_info[1]
                            # 公司介绍信息
                            job['business_info'] = company_info[2]

                            # 测试
                            print(job['business_name'])
                            # 写入List中
                            jobs.append(job)

                        except (IndexError, TypeError) as err:
                            logger.error(err)
                            error_list = [item['positionId'], item['companyId'], item]
                            self.err_list.append(error_list)
                            logger.info(error_list)

                    logger.info("%s职位, 第%d页成功" % (self._keyword, page))
                    logger.info("共 %d 条数据" % len(jobs))
                    time.sleep(random.uniform(2, 4))
                else:
                    time.sleep(random.uniform(4, 9))
            else:
                # 有时候会弹出个页面...不知道为什么
                logger.debug("暂停一下...")
                time.sleep(random.uniform(2, 4))
                self.parse()
        return jobs

    def get_job_info(self, job_id: str, cookies: dict) -> str:
        """
        职位信息
        :param job_id:
        :param cookies:
        :return:
        """
        url = 'https://www.lagou.com/jobs/%s.html' % job_id
        try:
            # 转换cookies
            response = requests.get(url,
                                    headers=self._headers,
                                    timeout=3,
                                    allow_redirects=False,
                                    cookies=cookies)
            if response.status_code == 302:
                self.get_job_info(job_id=job_id, cookies=self.all_cookies)

            html = response.content.decode("UTF-8")
            selector = etree.HTML(html)
            info = [str(x.encode("UTF-8"), encoding="UTF-8").replace("\xa0", "")
                    for x in selector.xpath("//dd[@class='job_bt']//p/text()")]
            info = self.get_value(info)
            if info != '':
                info = ''.join(info)
            else:
                self.get_job_info(job_id=job_id, cookies=self.all_cookies)
            return info
        except IndexError:
            self.get_job_info(job_id=job_id, cookies=self.all_cookies)
        except KeyError as err:
            logger.debug("Error---2")
            logger.error(err)

    def get_company_rate(self, company_id: str, cookies=None) -> list:
        """
        公司信息
        :param company_id:
        :param cookies:
        :return:
        """
        url = 'https://www.lagou.com/gongsi/%s.html' % company_id
        # try:
        # 请求
        response = requests.get(url,
                                headers=self._headers,
                                timeout=3,
                                allow_redirects=False,
                                cookies=cookies)
        # 判断状态码
        if response.status_code == 302:
            self.get_company_rate(company_id=company_id, cookies=self.company_cookies)

        html = response.content.decode("UTF-8")
        selector = etree.HTML(html).xpath('//*[@id="companyInfoData"]/text()')[0]

        # 解析json
        business_json = json.loads(selector, object_pairs_hook=OrderedDict)

        # 公司地址(判断)
        try:
            address_list = business_json['addressList'][0]
            business_location = \
                address_list['province'] + address_list['city'] + address_list['district']
        except KeyError:
            try:
                address_list = business_json['addressList'][1]
                business_location = \
                    address_list['province'] + address_list['city'] + address_list['district']
            except KeyError:
                business_location = ""

        # 公司网站主页
        business_website = business_json['coreInfo']['companyUrl']

        # 公司介绍
        business_info = business_json['introduction']['companyProfile']
        business_info = \
            self.filter_html_tag(content=business_info).replace("\n", "").replace("&nbsp;", "")

        # 返回
        result = [business_website, business_location, business_info]
        print(result)
        return result

    @staticmethod
    def filter_html_tag(content: str) -> str:
        """
        过滤文字中的HTML标签
        :param content:
        :return:
        """
        pattern = re.compile(r'<[^>]+>', re.S)
        return pattern.sub('', content)

    @staticmethod
    def get_value(data) -> str:
        """
        判断是否为空
        :param data:
        :return:
        """
        return data if data else ''
