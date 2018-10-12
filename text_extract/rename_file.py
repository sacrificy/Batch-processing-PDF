import os
import fitz
import re


def rename(path):
    name = []
    data = r'[1-9][0-9]{3}.*[0-9]{1,2}.*[0-9]{1,2}'
    for file in os.listdir(path):
        if file[-4:] == ".pdf":
            doc = fitz.open(os.path.join(path, file))
            page_count = doc.pageCount
            page = doc.loadPage(1)
            page_text = page.getText()
            fdata = re.findall(data, page_text)



            


