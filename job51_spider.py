# -*- coding = utf-8 -*-
# @Time : 2020/11/10 19:20
# @Author : Bruce Yang
# @File : job51_spider.py
# @Software : PyCharm
# @Description : 51job网站招聘信息爬取

import datetime
import json
import re

import requests
from bs4 import BeautifulSoup

# 正则
search_result = re.compile(r',"engine_search_result":(.*?),"jobid_count":"', re.S)

header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/86.0.4240.75 Safari/537.36"
}


# 查询岗位
def search_job(jobName, qry_pages):
    """
    :param jobName: 岗位名称
    :param qry_pages: 查询页面总数
    :return: 岗位列表Json
    """
    start_time = datetime.datetime.now()

    if qry_pages is None:
        qry_pages = 10

    try:
        qry_pages = int(qry_pages)
        if qry_pages <= 0:
            return "页面总数必须大于0！"
    except Exception as e:
        error_msg = f"页面总数{qry_pages}非数字，{e}"
        print(error_msg)
        return error_msg

    job_list = []
    # 取50页数据，知道某一页数据为0时
    for index in range(qry_pages):
        # for index in range(1, 2):


        print("查询第%d页。。。" % (index + 1))
        # 南京
        # url = 'https://search.51job.com/list/070200,000000,0000,00,9,99,' + str(jobName) + ',2,' + str(
        # 江北新区&&浦口
        # url = 'https://search.51job.com/list/070200,070207,0000,00,9,99,' + str(jobName) + ',2,' + str(
        # 江北新区&&浦口 && 工资15-20k && 20-30k
        url = 'https://search.51job.com/list/070200,070207%252c070214,0000,00,9,08%252c09,' + str(jobName) + ',2,' + str(
        # 深圳
        # url = 'https://search.51job.com/list/040000,000000,0000,00,9,99,' + str(jobName) + ',2,' + str(
        # 武汉
        # url = 'https://search.51job.com/list/180200,000000,0000,00,9,99,' + str(jobName) + ',2,' + str(
            index + 1) + '.html'
        html = get_page_html(url)
        # print(html)

        # 通过正则找到招聘公司数据
        jobs_result = re.findall(search_result, html)
        # print(jobs_result[0])

        # 进行json格式的编码, 将列表转化为字符串
        json_str = json.dumps(jobs_result[0])
        # print(json_str)
        # 将 JSON 数组转换为 Python 字典（解析数组调用两次json的loads方法）
        data = json.loads(json.loads(json_str))
        print("岗位数：%d" % len(data))
        if len(data) <= 0:
            print("没有数据了，查询结束")
            break

        for iData in data:
            # print(iData)
            '''
            {'type': 'engine_search_result', 'jt': '0', 'tags': [], 'ad_track': '', 'jobid': '125201993', 
            'coid': '5753461', 'effect': '1', 'is_special_job': '', 'job_href': 'https://jobs.51job.com/nanjing-xwq/125201993.html?s=01&t=0',
             'job_name': 'Python开发工程师', 'job_title': 'Python开发工程师', 'company_href': 'https://jobs.51job.com/all/co5753461.html',
             'company_name': '江苏国密数字认证有限公司', 'providesalary_text': '0.9-1.4万/月', 'workarea': '070201', 
             'workarea_text': '南京-玄武区', 'updatedate': '11-12', 'isIntern': '', 'iscommunicate': '', 
             'companytype_text': '民营公司', 'degreefrom': '6', 'workyear': '4', 'issuedate': '2020-11-12 04:00:44', 'isFromXyz': '', 
             'jobwelf': '五险一金 绩效奖金 周末双休 节日福利', 'jobwelf_list': ['五险一金', '绩效奖金', '周末双休', '节日福利'], 
            'attribute_text': ['南京-玄武区', '2年经验', '本科', '招1人'], 'companysize_text': '少于50人', 'companyind_text': '互联网/电子商务', 'adid': ''}
            '''
            job_item = {'company_name': iData['company_name'],
                        'job_name': iData['job_name'],
                        'workarea_text': iData['workarea_text'],
                        'companysize_text': iData['companysize_text'],
                        'providesalary_text': iData['providesalary_text'],
                        'attribute_text': iData['attribute_text'],
                        'job_href': iData['job_href'],
                        'job_info': job_detail(iData['job_href'])}
            # print(job_item)
            job_list.append(job_item)

    end_time = datetime.datetime.now()
    print("查询岗位总耗时%d秒" % (end_time - start_time).seconds)

    return json.dumps(job_list)


# 工作详情
def job_detail(job_url):
    html = get_page_html(job_url)
    bs = BeautifulSoup(html, "html.parser")
    infos = bs.select('.tCompany_main > .tBorderTop_box > .bmsg.job_msg.inbox > p')
    info_str = ""
    for i in infos:
        # print(type(i))
        # print(i.get_text())
        info_str += i.text.strip() + "\n"

    address = bs.select('.tCompany_main > .tBorderTop_box > .bmsg.inbox > .fp')
    address_str = ""
    for ii in address:
        address_str += ii.text.strip()

    job_info = f'职位信息：\n{info_str}\n{address_str}'
    # print(job_info)
    return job_info


# 获取页面html
def get_page_html(url):
    r = requests.get(url, headers=header)
    r.encoding = 'gbk'
    return r.text


if __name__ == '__main__':
    job = input("请输入要搜索的职位：")
    pages = input("请输入查询总页数：")
    search_job(job, pages)
