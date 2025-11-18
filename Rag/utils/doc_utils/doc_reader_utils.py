import fitz  # PyMuPDF

def read_pdf(file_path):
    text = ""
    # 打开 PDF 文件
    doc = fitz.open(file_path)
    #print(f"PDF 页数: {doc.page_count}")
    # 逐页提取文本
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        page_text = page.get_text()

        text += f"\n--- 第 {page_num + 1} 页 ---\n"
        text += page_text

    doc.close()
    return text

def read_basic(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    return text

DOC_READERS = {
    ".txt": read_basic,
    ".pdf": read_pdf,
    ".md": read_basic
}