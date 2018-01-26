# 拉勾网爬虫(非Scrapy版)

---

<h3 id="Env">环境和安装方式</h3>

* 开发环境: Win10 x64
* Python版本: Python3.4.4
* Python依赖:
    * lxml
    * requests

* 安装方式:

```Bash
pip install -r requirements.txt
```

---

<h3 id="TimeLine">进度</h3>

* 2018-01-26:
    * 实现搜索任意职位获取数据,且字段众多(字段列表见下)
    * 代码风格遵循Type hint风格
    * 一些细节待完善(目前还没写写入数据库的方法, 将在这一两天内完善)

---

<h3 id="Future">未来进度</h3>

* 数据库(MongoDB、Mysql等)
* 进度监控
* 完善上述两点后迁移到Scrapy上.

---

<h3 id="Plus">补充</h3>

* 项目中的lagou_login代码来自 [拉勾网的模拟登录](https://github.com/laichilueng/lagou_login)