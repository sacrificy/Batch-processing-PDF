import os
import fitz
import re
import shutil
from operator import itemgetter
from itertools import groupby


def mkdir(path):
    '''
    新建目录
    :param path:要创建的路径
    :return:
    '''
    # 去除首位空格
    path = path.strip()
    # 去除尾部 \ 符号
    path = path.rstrip("\\")

    # 判断路径是否存在
    # 存在     True
    # 不存在   False
    isExists = os.path.exists(path)
    # 判断结果
    if not isExists:
        # 如果不存在则创建目录
        # 创建目录操作函数
        os.makedirs(path)
        return True
    else:
        # 如果目录存在则不创建
        return False

# 对文件进行预处理，分成资料来源，数据来源，来源三种情况
def preprocess(path):
    '''
    在截取图片之前对数据进行预处理
    :param path:文件路径
    :return:分类后的文件夹
    '''
    materialsource = []
    datasource = []
    source = []
    mkpath1 = path + "/资料来源"
    mkpath2 = path + "/数据来源"
    mkpath3 = path + "/来源"
    pathdir = {"资料来源：":mkpath1, "数据来源：":mkpath2, "来源：":mkpath3}
    mkdir(mkpath1)
    mkdir(mkpath2)
    mkdir(mkpath3)
    for file in os.listdir(path):
        if file[-4:] == '.pdf':
            doc = fitz.open(os.path.join(path, file))
            page_count = doc.pageCount
            for i in range(1, page_count):
                page = doc.loadPage(i)
                materialsource = materialsource.extend(page.searchFor("资料来源："))
                datasource = materialsource.extend(page.searchFor("数据来源："))
                source = materialsource.extend(page.searchFor("来源："))
            doc.close()
        if len(materialsource) != 0 and len(datasource) == 0:
            shutil.copy(os.path.join(path, file), os.path.join(mkpath1, file))
        if len(materialsource) == 0 and len(datasource) != 0:
            shutil.copy(os.path.join(path, file), os.path.join(mkpath2, file))
        if len(materialsource) == 0 and len(datasource) == 0 and len(source) != 0:
            shutil.copy(os.path.join(path, file), os.path.join(mkpath3, file))
    return pathdir    

# 处理截取的重复数据
def deal_repeat(list):
    length = len(list)
    # 标记数组用来判断重复数据
    sign = [0]
    sign = sign * length
    # 存放处理完的坐标
    result = []
    for i in range(0, length - 1):
        count = 0
        x0 = abs(list[i].x0 - list[i + 1].x0)
        x1 = abs(list[i].x1 - list[i + 1].x1)
        y0 = abs(list[i].y0 - list[i + 1].y0)
        y1 = abs(list[i].y1 - list[i + 1].y1)
        # print('坐标之间的差值--', x0, y0, x1, y1)
        if x0 < 3:
            count += 1
        if x1 < 3:
            count += 1
        if y0 < 3:
            count += 1
        if y1 < 3:
            count += 1
        if count == 4:
            sign[i] += 1
            sign[i+1] += 2
    # 用来筛选重复数据
    for i in range(length):
        if sign[i] <= 1:
            result.append(list[i])
    return result


def deal_reContext(list1, list2):
    # length1表示截图图表的数组长度
    # length2表示截图资料来源的数组长度
    length1 = len(list1)
    length2 = len(list2)
    result = []
    if length2 != length1:
        for j in range(length2):
            # 保存两个坐标之间纵坐标只差
            pMin = 900.00
            temp = fitz.Rect(0, 0, 0, 0)
            for i in range(length1):
                if list2[j].y0 > list1[i].y0:
                    height = abs(list1[i].y0 - list2[j].y0)
                    # print(height)
                    if pMin > height:
                        pMin = height
                        temp = list1[i]
            result.append(temp)
    else:
        result = list1
    return result


# 除去字符串中的非法字符
def validateTitle(title):
    rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
    new_title = re.sub(rstr, "_", title)  # 替换为下划线
    return new_title


def image_extract(path):
    keywords = "........"
    for file in os.listdir(path):
     # try:
        if file[-4:] == ".pdf":
            mkpath = 'E:\\项目\\试运行\\201808\\提取图片\\待处理\\提取图片\\'
            mkpath = mkpath + file[:-4] + '\\'
            mkdir(mkpath)
            doc = fitz.open(os.path.join(path, file))
            page_count = doc.pageCount
            picname_num = 0
            picname_list = []
            for i in range(10):
                page = doc.loadPage(i)
                page_text = page.getText()
                if keywords in page_text:
                    pattern = re.compile(r'图表 [0-9][^\...]*')
                    picname_list1 = pattern.findall(page_text)
                    picname_list.extend(picname_list1)
            # 处理具体每一页的图表
            for i in range(1, page_count):
                page = doc.loadPage(i)
                page_text = page.getText()
                if keywords in page_text:
                    pattern = re.compile(r'图表 [0-9][^\.]*')
                    picname_list1 = pattern.findall(page_text)
                    picname_list.extend(picname_list1)
                # 获取每一页中关键字列表
                pic_1 = page.searchFor("图表")
                data_1 = page.searchFor("资料来源：")
                # print('未处理前---第', i, '页--图表的个数为', len(pic_1))
                # print('未处理前---第', i, '页--数据来源的个数为', len(data_1))
                # 处理重复数据
                pic_2 = deal_repeat(pic_1)
                data = deal_repeat(data_1)
                # print('未处理正文重复----第', i, '页--图表的个数为', len(pic_2))
                # print('未处理正文重复--图表坐标', pic_2)
                # print('未处理正文重复--资料来源坐标', data)
                # print('第', i, '页--数据来源的个数为', len(data))
                # 处理正文出现的重复数据
                pic = deal_reContext(pic_2, data)
                # print('处理完正文重复----第', i, '页--图表的个数为', len(pic))
                # print('处理完正文重复----图表坐标', pic)
                # print('处理完正文重复----资料来源坐标', data)
                # print('第', i, '页--数据来源的个数为', len(data))
                pic_len = len(pic)
                data_len = len(data)
                # 排除一些不可能的情况
                if pic_len == 0 and data_len == 0:
                    continue
                if abs(pic_len - data_len) > 5:
                    continue

                mat = fitz.Matrix(3, 3)  # 缩放
                page_ = page.rect  # 页面大小
                page_width = page_.x1  # 页面宽
                page_length = page_.y1  # 页面宽

                if pic_len > data_len:  # 图表数多于资料来源
                    pic = pic[:data_len - pic_len]

                elif pic_len < data_len:  # 资料来源多于图表数
                    for i in range(data_len - pic_len):
                        pic.insert(0, fitz.Rect(0, 0, 0, 0))

                if pic_len == data_len:
                    pic1 = [[]]
                    data1 = [[]]
                    for j in range(pic_len):  # 将图表按行分组
                        if j < (pic_len - 1):
                            if abs(pic[j].y0 - pic[j + 1].y0) < 2.5:  # 若果两个数据再一组不能严格的相等，要有一个浮动区间
                                pic1[-1].append(pic[j])
                                data1[-1].append(data[j])
                            else:
                                pic1[-1].append(pic[j])
                                pic1.append([])
                                data1[-1].append(data[j])
                                data1.append([])
                    pic1[-1].append(pic[j])
                    data1[-1].append(data[j])

                    picgroup_num = len(pic1)  # 图片组数

                    for k in range(picgroup_num):  # 按组处理图片
                        pic1_len = len(pic1[k])
                        for j in range(pic1_len):
                            if j < pic1_len - 1:
                                if data1[k][j].x0 < pic1[k][j].x0:
                                    clip = fitz.Rect(data1[k][j].x0 - 5, pic1[k][j].y0 - 2, data1[k][j + 1].x0 - 18,
                                                     data1[k][j].y1)
                                else:
                                    clip = fitz.Rect(pic1[k][j].x0 - 5, pic1[k][j].y0 - 2, pic1[k][j + 1].x0 - 18,
                                                     data1[k][j].y1)
                                print('第', picname_num, '个图片--截取坐标的 x0', data1[k][j].x0 - 5, '截取坐标的 y0', pic1[k][j].y0 - 5, '截取坐标的 x1', data1[k][j + 1].x0 - 18, '截取坐标的 y1', data1[k][j].y1)
                                pix = page.getPixmap(matrix=mat, clip=clip, alpha=False)
                                # print(pix)
                                # 预处理字符串中的非法字符
                                # deal_name = validateTitle(picname_list[picname_num])
                                # fn = deal_name + ".png"
                                fn = '图表 ' + str(picname_num) + ".png"
                                pix.writePNG(os.path.join(mkpath, fn))
                                picname_num = picname_num + 1
                            else:
                                if data1[k][j].x0 < pic1[k][j].x0:
                                    clip = fitz.Rect(data1[k][j].x0 - 5, pic1[k][j].y0-2, page_width - 20,
                                                     data1[k][j].y1)
                                else:
                                    clip = fitz.Rect(pic1[k][j].x0 - 5, pic1[k][j].y0 - 2, page_width - 20,
                                                     data1[k][j].y1)
                                print('这组的最后一个 第', picname_num, '个图片--截取坐标的 x0', data1[k][j].x0 - 5, '截取坐标的 y0',
                                      pic1[k][j].y0 - 5, '截取坐标的 x1', page_width - 49, '截取坐标的 y1',
                                      data1[k][j].y1)
                                pix = page.getPixmap(matrix=mat, clip=clip, alpha=False)
                                # deal_name = validateTitle(picname_list[picname_num])
                                # fn = deal_name + ".png"
                                fn = '图表 ' + str(picname_num) + ".png"
                                pix.writePNG(os.path.join(mkpath, fn))
                                picname_num = picname_num + 1
            doc.close()
            shutil.copy(os.path.join(path, file), os.path.join(mkpath, file))
     # except:
     #    #print(file)
     #    mkdir(path + '\\未处理完成')
     #    shutil.move(mkpath, path + '\\未处理完成')
     #    continue


image_extract("E:\\项目\\试运行\\201808\\提取图片\\待处理")
