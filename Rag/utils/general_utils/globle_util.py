import hashlib


# 生成hash值
def gen_hash(text):
    return hashlib.md5(text.encode('utf-8')).hexdigest()

# 流式打印
def stream_print(generator):
    for chunk in generator:
        print(chunk, end="", flush=True)

if __name__ == '__main__':
    print(len(gen_hash("123")))