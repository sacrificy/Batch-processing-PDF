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
    keyword1 = r'(^[图表]+\s*[表]*\s*\d+.*?)(\.{2,})(\s*\d+)'
    num = 0
    flag = 0
    for i in range(search_pages):
        page = doc.loadPage(i)
        page_text = page.getText()
        # print(page_text)
        if keyword in page_text:
            num=1
            pattern = re.compile(keyword1,re.M)
            temp_list = pattern.findall(page_text)
            result.extend(temp_list)
            if len(temp_list):
                if int(temp_list[0][2]) <= i+1:
                    flag=1
        else:
            if num == 1:
                num = i
            continue
    return result,num,flag

# 参数需要上一个函数处理完之后的目录列表
def catalog_list_grouping(list):
    dic = {}
    # split_keyword = r'\.+'
    for item in list:
        # pattern = re.compile(split_keyword)
        # temp_list = pattern.split(item)
        # strinfo = re.compile('\s+')
        # page = strinfo.sub('', temp_list[-1])
        page=item[2]
        page=page.strip()
        name=item[0]
        name=name.rstrip()
        if page in dic:
            dic[page].append(name)
        else:
            dic[page] = [name]

    return dic





if __name__ == '__main__':
    file_name = 'D:/666.pdf'
    lists,first_page,flag = catalog_extract(file_name)
    # for x in lists:
    #     print(x[0],x[2])
    dis = catalog_list_grouping(lists)
    # print(dis)
    # print(dis)
    # for i in range(len(list)):
    #     print('list序号', i, 'list内容：', list[i])