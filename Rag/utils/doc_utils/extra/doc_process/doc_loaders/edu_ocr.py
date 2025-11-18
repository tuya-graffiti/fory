import os,paddle
'''
paddleocr：解析图片中的文字，也可以进行表格识别
rapidocr_paddle 和 rapidocr_onnxruntime 两种导入方式
主要区别在于它们所使用的推理引擎和硬件支持
选择哪种方式最合适取决于你的硬件环境和性能需求。
当你有 GPU 且追求速度时：使用 rapidocr_paddle。PaddlePaddle 原生支持在 GPU 上推理 PaddleOCR 模型，速度更快。
当只有 CPU 且需要高效推理时：使用 rapidocr_onnxruntime。它在 CPU 上进行了优化，资源占用较低.
'''

def get_ocr(use_cuda: bool = True):
    # paddle_dir = os.path.dirname(os.path.dirname(paddle.__file__))
    # # 构建正确的 cudnn bin 目录路径
    # cudnn_bin_path = os.path.join(paddle_dir, 'paddle', 'nvidia', 'cudnn', 'bin')
    # if os.path.exists(cudnn_bin_path):
    #     os.add_dll_directory(cudnn_bin_path)
    try:
        from rapidocr_paddle import RapidOCR
        '''
        det_use_cuda=True：启用检测模型的GPU加速。cls_use_cuda=True：启用分类模型的GPU加速。rec_use_cuda=True：启用识别模型的GPU加速。
        '''
        ocr = RapidOCR(det_use_cuda=use_cuda, cls_use_cuda=use_cuda, rec_use_cuda=use_cuda)
    except ImportError:
        print("rapidocr_paddle not found, try to use rapidocr_onnxruntime")
        from rapidocr_onnxruntime import RapidOCR
        ocr = RapidOCR()
    return ocr


if __name__ == "__main__":
    a = get_ocr( True)
    from PIL import Image

    img = Image.open(r"D:\workspace\pythonworkspace\chuanzhi\rag_project\utils\doc_parse\images\page3_2.png")
    #path = r"D:\workspace\pythonworkspace\chuanzhi\rag_project\utils\doc_parse\images\page3_2.png"
    a = a( img)
    print( a)