#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import fitz
import re
import shutil


# 首先得先对PDF进行目录的提取，用来保存需要查找的图表关键字
# 参数需要放入文件名
def catalog_extract(file_name):
    doc = fitz.open(file_name)
    page_count = doc.pageCount
    result = []
    if page_count > 10:
        search_pages = 10
    else:
        search_pages = page_count
    keyword = '.......'
    keyword1 = r'(?:图\s*表|表|图)\s*[0-9]+[^\...]*\.+\s*\d+'
    for i in range(search_pages):
        page = doc.loadPage(i)
        page_text = page.getText()
        if keyword in page_text:
            pattern = re.compile(keyword1)
            temp_list = pattern.findall(page_text)
            result.extend(temp_list)
        else:
            continue
    return result


# 参数需要上一个函数处理完之后的目录列表
def catalog_list_grouping(list):
    dic = {}
    split_keyword = r'\.+'
    for item in list:
        pattern = re.compile(split_keyword)
        temp_list = pattern.split(item)
        strinfo = re.compile('\s+')
        page = strinfo.sub('', temp_list[-1])
        if page in dic:
            dic[page].append(temp_list[0])
        else:
            dic[page] = [temp_list[0]]

    return dic





if __name__ == '__main__':
    file_name = 'D:/Study/工程项目/测试文件/20180803-信达证券-氢能源系列报告之一：产业化迎来真实导入期.pdf'
    list = catalog_extract(file_name)
    dis = catalog_list_grouping(list)
    print(dis)
    # for i in range(len(list)):
    #     print('list序号', i, 'list内容：', list[i])