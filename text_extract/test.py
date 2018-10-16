import fitz
from catalog_grouping import catalog_extract,catalog_list_grouping
import operator
from itertools import groupby
import re
import os

def image_extract(file_path,out_path,fig_name,file_type,first_page,flag):
    doc=fitz.open(file_path)
    # page=doc.loadPage(15)
    # page_count=doc.pageCount
    # print(page.getText())
    out_path=os.path.join(out_path,os.path.basename(file_path))
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    Source_type=["来源","资料来源","数据来源"]
    Offset=1
    if flag == 1:
        Offset=-first_page+1
    for page_num,fig_list in fig_name.items():
        # print(page_num,fig_list)
        name_figrects=[]
        page=doc.loadPage(int(page_num)-Offset)
        page1=doc.loadPage(int(page_num)-Offset+1)
        page_ = page.rect  # 页面大小
        page_length = page_.x1  # 页面长
        page_width = page_.y1  # 页面宽
        source_rects=[x.round() for x in page.searchFor(Source_type[file_type])]
        source_rects_1=[x.round() for x in page1.searchFor(Source_type[file_type])]
        for fig in fig_list:
            fig_rect=search_fig(page,fig)
            name_figrect=[fig,fig_rect[0]]
            name_figrects.append(name_figrect)
        name_figrect_sourcerects,rest_name_figrect=match_fig_source(name_figrects,source_rects,page_length,page_width)
        if len(rest_name_figrect):
            extra_rest_fig(page,page1,source_rects_1,rest_name_figrect,page_length,page_width,out_path)
        if len(name_figrect_sourcerects):
            name_figrect_sourcerect_row=group_name_figrect_sourcerects(name_figrect_sourcerects)
            name_rects=make_rect(name_figrect_sourcerect_row,page_length,page_width)
            extract_fig(page,name_rects,out_path)
        # print(page_num,name_figrect_sourcerects)
        
        # extract_fig(fig_sources,page_length,page_width)
        # print(name_figrects)
        # print(name_figrect_sourcerects)
        # for i in name_figrect_sourcerects: /名字 图片  rect
        #     print(i[0],len(i[1]),len(i[2]))
        # for i in name_figrect_sourcerect_row:
        #     print('页数',page_num,'分组',len(name_figrect_sourcerect_row))
        # break

def search_fig(page,fig):
    fig_rect=page.searchFor(fig[0:10])#直接根据目录匹配
    a=0
    if not len(fig_rect):#根据图表+数字匹配
        a=1
        fig_num_r = r'(图\s*表|表|图)\s*\d+'
        pattern = re.compile(fig_num_r)
        fig_num=pattern.match(fig).group(0)
        fig_rect=page.searchFor(fig_num)
        if not len(fig_rect):#根据图表+数字去掉空格匹配
            a=2
            # front = r'([图表]+\s*[图表]*\d+)(\s*[：.:]?\s*)(.+)'
            fig_num1=re.sub('\s','',fig_num)
            fig_rect=page.searchFor(fig_num1)
    if not len(fig_rect):#根据图表名的一部份匹配
        a=3
        name_r=r'[\u4e00-\u9fa5]{3,}'
        pattern1 = re.compile(name_r)
        name=pattern1.findall(fig)
        if not len(name):
            name_=name[0]
            for x in name:
                if len(name_)<len(x):
                    name_=x
            fig_rect=page.searchFor(name_)
        
        
    if not len(fig_rect):#搜索不到截取一整页
        a=4
        fig_rect=[fitz.Rect(-1,-1,-1,-1)]
    print(a,fig,len(fig_rect))
    fig_rect=[x.round() for x in fig_rect]
    # print(fig,fig_rect)
    return fig_rect


def match_fig_source(name_figrects,source_rects,page_length,page_width):
    rest_name_figrect=[]
    match=[]
    for name_figrect in name_figrects:
        fig_source=fitz.Rect(page_length,page_width,page_length,page_width)
        for source in source_rects:
            if source.y0>name_figrect[1].y0:
                if name_figrect[1].tl.distance_to(source.tl)<name_figrect[1].tl.distance_to(fig_source):
                    fig_source=source
        if fig_source == fitz.Rect(page_length,page_width,page_length,page_width):
            rest_name_figrect.append(name_figrect)
        else:
            match.append([name_figrect[0],name_figrect[1],fig_source])
    return match,rest_name_figrect

def extra_rest_fig(page,page1,source_rects_1,rest_name_figrect,page_length,page_width,out_path):
    mat = fitz.Matrix(3, 3)
    rest_name_figrect=sorted(rest_name_figrect,key=take_x0)
    if len(rest_name_figrect)>len(source_rects_1):
        for i in range(len(rest_name_figrect)-len(source_rects_1)):
            source_rects_1.append(fitz.Rect(0,0,page_length,page_width))        
    for i in range(len(rest_name_figrect)):
        if i < len(rest_name_figrect) - 1:
            rect1=fitz.Rect(source_rects_1[i].x0 - 8, rest_name_figrect[i][1].y0, source_rects_1[i+1].x0 - 18,page_width-60)
            rect2=fitz.Rect(source_rects_1[i].x0 - 8,60, source_rects_1[i+1].x0 - 18,source_rects_1[i].y1)
            deal_name = validateTitle(rest_name_figrect[i][0])
            fig_name = deal_name + ".png"
            pix = page.getPixmap(matrix=mat, clip=rect1, alpha=False)
            pix1 = page1.getPixmap(matrix=mat, clip=rect2, alpha=False)
            tar_irect  = fitz.IRect(0, 0, pix.width,pix.height+pix1.height)
            tar_pix  = fitz.Pixmap(fitz.csRGB, tar_irect, pix.alpha)
            tar_pix.clearWith(90)
            pix.x=0
            pix.y=0
            pix1.x=0
            pix1.y=pix.height
            tar_pix.copyPixmap(pix,pix.irect)
            tar_pix.copyPixmap(pix1,pix1.irect)
            tar_pix.writePNG(os.path.join(out_path, fig_name))
        else:
            rect1=fitz.Rect(source_rects_1[i].x0 - 8, rest_name_figrect[i][1].y0,page_length - 49,page_width-60)
            rect2=fitz.Rect(source_rects_1[i].x0 - 8,60, page_length - 49,source_rects_1[i].y1) 
            deal_name = validateTitle(rest_name_figrect[i][0])
            fig_name = deal_name + ".png"
            pix = page.getPixmap(matrix=mat, clip=rect1, alpha=False)
            pix1 = page1.getPixmap(matrix=mat, clip=rect2, alpha=False)
            tar_irect  = fitz.IRect(0, 0, pix.width,pix.height+pix1.height)
            tar_pix  = fitz.Pixmap(fitz.csRGB, tar_irect, pix.alpha)
            tar_pix.clearWith(90)
            pix.x=0
            pix.y=0
            pix1.x=0
            pix1.y=pix.height
            tar_pix.copyPixmap(pix,pix.irect)
            tar_pix.copyPixmap(pix1,pix1.irect)
            tar_pix.writePNG(os.path.join(out_path, fig_name))


def group_name_figrect_sourcerects(name_figrect_sourcerects):
    # print(name_figrect_sourcerects)
    name_figrect_sourcerects=sorted(name_figrect_sourcerects,key=take_y0_x0)

    name_figrect_sourcerect_row=[[]]
    length = len(name_figrect_sourcerects)  # 图表数
    for i in range(length):  # 将图表按行分组
        if i < (length - 1):
            if name_figrect_sourcerects[i][1].y0 == name_figrect_sourcerects[i+1][1].y0:
                name_figrect_sourcerect_row[-1].append(name_figrect_sourcerects[i])
            else:
                name_figrect_sourcerect_row[-1].append(name_figrect_sourcerects[i])
                name_figrect_sourcerect_row.append([])
    name_figrect_sourcerect_row[-1].append(name_figrect_sourcerects[i])

    # print(name_figrect_sourcerects)
    # print(name_figrect_sourcerect_row)
    return name_figrect_sourcerect_row
    

def extract_fig(page,name_rects,out_path):
    mat = fitz.Matrix(3, 3)
    for name_rect in name_rects:
        deal_name = validateTitle(name_rect[0])
        pix = page.getPixmap(matrix=mat, clip=name_rect[1], alpha=False)
        fig_name = deal_name + ".png"
        pix.writePNG(os.path.join(out_path, fig_name))
        # print(name_rect[0],name_rect[1])


def take_y0_x0(elem):
    # print(elem)
    return elem[1].y0,elem[1].x0

def take_x0(elem):
    # print(elem)
    return elem[1].x0

def make_rect(name_figrect_sourcerect_row,page_length,page_width):
    name_rects=[]
    for row in name_figrect_sourcerect_row:
        for i in range(len(row)):
            if i < len(row) - 1:
                clip = fitz.Rect(row[i][2].x0 - 8, row[i][1].y0, row[i+1][2].x0 - 18,row[i][2].y1)
                name_rects.append([row[i][0],clip])
            else:
                clip = fitz.Rect(row[i][2].x0 - 8, row[i][1].y0, page_length - 49,row[i][2].y1)
                name_rects.append([row[i][0],clip])
    # print(name_rects)
    return name_rects

def validateTitle(title):
    rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
    new_title = re.sub(rstr, "_", title)  # 替换为下划线
    return new_title


if __name__ == "__main__":
    file_path="D:/资料来源/"
    out_path="D:/pic/"
    pdf_files = [name for name in os.listdir(file_path) if name.endswith('.pdf')]
    for pdf in pdf_files:
        pdf_path=os.path.join(file_path,pdf)
        file_type=1
        name_list,first_page,flag = catalog_extract(pdf_path)
        fig_name = catalog_list_grouping(name_list)
        image_extract(pdf_path,out_path,fig_name,file_type,first_page,flag)

    # file_type=1
    # name_list,first_page,flag = catalog_extract('D:/666.pdf')
    # fig_name = catalog_list_grouping(name_list)
    # print(fig_name)
    # image_extract('D:/666.pdf',out_path,fig_name,file_type,first_page,flag)

    
