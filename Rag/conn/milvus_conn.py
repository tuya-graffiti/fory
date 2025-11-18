from pymilvus import MilvusClient
from base import config_gen as cfg

# 前端：http://47.108.85.255:8000/
class MilvusConn:
    def __init__(self,db_name=cfg.MILVUS.DATABASE_NAME):
        self.client = MilvusClient(uri=f"http://{cfg.MILVUS.HOST}:{cfg.MILVUS.PORT}",
                                   db_name=db_name)

    def close(self):
        self.client.close()

    def list_collections(self):
        return self.client.list_collections()

    def get_all_chunks(self,collection_name, batch_size=24):
        all_chunks = []
        offset = 0
        while True:
            # 分页查询
            results = self.client.query(
                collection_name=collection_name,
                filter="",
                output_fields=["*"],
                offset=offset,
                limit=batch_size
            )

            if not results:
                break
            all_chunks.extend(results)
            offset += len(results)

            yield results
            # 检查是否达到最大记录数或没有更多数据
            if len(results) < batch_size:
                break






if __name__ == "__main__":
    miC = MilvusConn()
    # 测试是否连接成功
    print(miC)