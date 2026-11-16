import os.path

import pdfplumber
from concurrent.futures import ThreadPoolExecutor
import glob


# 打开PDF文件并读取其内容
def pdf2txt(pdf_path):
    save_class_dir = os.path.basename(os.path.dirname(pdf_path))  # pdf文件所在目录
    save_name = os.path.basename(pdf_path).replace('.pdf', '.txt') # 保存的文件名
    save_path = os.path.join(r"txts",save_class_dir, save_name) # 保存路径
    # 创建文件夹
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    print(save_path)
    if os.path.exists(save_path):
        return
    _str = ""  # 保存每页的内容
    with pdfplumber.open(pdf_path) as pdf:
        # 遍历每个页面
        for index, page in enumerate(pdf.pages, start=1):
            # print(page.extract_text())
            res = page.extract_text()
            lines = res.splitlines()
            res = '\n'.join(lines)
            _str += res
    pdf_str = _str  # 保存所有页的内容

    with open(save_path, 'w', encoding="utf-8") as txt_file:  # 保存到txt文件
        txt_file.write(pdf_str)


if __name__ == '__main__':
    pool = ThreadPoolExecutor(max_workers=10)
    # 将文本写入新的TXT文件中
    glob_path = r"pdfs/*/*.pdf"
    file_list = glob.glob(glob_path)
    for file in file_list:
        pool.submit(pdf2txt, file)
