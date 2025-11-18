from conn import rerank_conn,milvus_conn
from pymilvus import DataType,AnnSearchRequest, WeightedRanker
from base import configs
from milvus_model.hybrid import BGEM3EmbeddingFunction
from datetime import datetime
from tqdm import tqdm
from utils.general_utils.globle_util import gen_hash
# 定义 VectorStore 类，封装向量存储和检索功能
class VectorStore:
    # 初始化方法，设置向量存储的基本参数
    def __init__(self):
        # 设置 Milvus 集合名称
        self.collection_name = "vector_store"
        self.rerank_model = rerank_conn.RerankModel()
        # 初始化 BGE-M3 嵌入函数，使用 CPU 设备，不启用 FP16
        self.emb_model = BGEM3EmbeddingFunction()
        # 获取稠密向量的维度
        self.dense_dim = self.emb_model.dim["dense"]
        # print("稠密向量的维度:", self.dense_dim)
        # 初始化 Milvus 客户端，连接到指定主机和数据库
        self.client = milvus_conn.MilvusConn().client
        # 调用方法创建或加载 Milvus 集合
        self._create_or_load_collection()

    # 定义私有方法，创建或加载 Milvus 集合
    def _create_or_load_collection(self):
        # 检查指定集合是否已存在
        if not self.client.has_collection(self.collection_name):
            # 创建集合 Schema，禁用自动 ID，启用动态字段
            schema = self.client.create_schema(auto_id=False, enable_dynamic_field=True)
            # 添加 ID 字段，作为主键，VARCHAR 类型，最大长度 100
            schema.add_field(field_name="id", datatype=DataType.VARCHAR, is_primary=True, max_length=64)
            # 添加文本字段，VARCHAR 类型，最大长度 65535
            schema.add_field(field_name="text", datatype=DataType.VARCHAR, max_length=65535)
            # 添加稠密向量字段，FLOAT_VECTOR 类型，维度由嵌入函数指定
            schema.add_field(field_name="dense_vector", datatype=DataType.FLOAT_VECTOR, dim=self.dense_dim)
            # 添加稀疏向量字段，SPARSE_FLOAT_VECTOR 类型
            schema.add_field(field_name="sparse_vector", datatype=DataType.SPARSE_FLOAT_VECTOR)
            # 添加父块 ID 字段，VARCHAR 类型，最大长度 100
            schema.add_field(field_name="parent_id", datatype=DataType.VARCHAR, max_length=32)
            # 添加父块内容字段，VARCHAR 类型，最大长度 65535
            schema.add_field(field_name="parent_content", datatype=DataType.VARCHAR, max_length=65535)
            # 添加学科类别字段，VARCHAR 类型，最大长度 50
            schema.add_field(field_name="source", datatype=DataType.VARCHAR, max_length=256)
            # 添加时间戳字段，VARCHAR 类型，最大长度 50
            schema.add_field(field_name="timestamp", datatype=DataType.FLOAT)

            # 创建索引参数对象
            index_params = self.client.prepare_index_params()
            # 为稠密向量字段添加 IVF_FLAT 索引，度量类型为内积 (IP)
            index_params.add_index(
                field_name="dense_vector",
                index_name="dense_index",
                index_type="IVF_FLAT",
                metric_type="COSINE",
                params={"nlist": 128}
            )
            # 为稀疏向量字段添加 SPARSE_INVERTED_INDEX 索引，度量类型为内积 (IP)
            index_params.add_index(
                field_name="sparse_vector",
                index_name="sparse_index",
                index_type="SPARSE_INVERTED_INDEX",
                metric_type="IP",
                params={"drop_ratio_build": 0.2}
            )

            # 创建 Milvus 集合，应用定义的 Schema 和索引参数
            self.client.create_collection(collection_name=self.collection_name, schema=schema,
                                         index_params=index_params)
        # 将集合加载到内存，确保可立即查询
        self.client.load_collection(self.collection_name)

    #整理稀疏向量
    def _prepare_sparse_vector(self, row):
        return {index: data for index, data in zip(row.indices,row.data)}

    #添加chunk
    def add_chunks(self,chunks):
        embeddings = self.emb_model.encode_documents([chunk["text"] for chunk in chunks])
        datas = []
        total_batchs = (len(chunks) + configs.batch_size - 1) // configs.batch_size
        for i in tqdm(range(0, len(chunks), configs.batch_size), desc="插入批次"):
            batch_chunks = chunks[i:i + configs.batch_size]
            batch_dense = embeddings["dense"][i:i + configs.batch_size]
            batch_sparse = embeddings["sparse"][i:i + configs.batch_size]
            for chunk, dense, sparse in zip(batch_chunks, batch_dense, batch_sparse):
                d = {
                    "id": gen_hash(chunk["text"]),
                    "text": chunk["text"],
                    "dense_vector": dense,
                    "sparse_vector": self._prepare_sparse_vector(sparse),
                    "source": chunk["source"],
                    "parent_id": chunk["parent_id"],
                    "parent_content": chunk["parent_content"],
                    "timestamp": datetime.now().timestamp()  # 时间戳
                }
                datas.append(d)
        self.client.upsert(collection_name=self.collection_name, data=datas)

    # 混合排序+父子排序
    def hybrid_search(self,query,c=configs.c):
        # c:召回出来的候选数量:
        # k:最终精排后的top k
        # 使用 BGE-M3 嵌入函数生成查询的嵌入
        query_embeddings = self.embedding_function([query])
        # 获取查询的稠密向量
        dense_query_vector = query_embeddings["dense"][0]
        # 初始化查询的稀疏向量
        sparse_query_vector = self._prepare_sparse_vector(query_embeddings["sparse"]._getrow(0))

        # 创建稠密向量搜索请求
        dense_request = AnnSearchRequest(
            data=[dense_query_vector],
            anns_field="dense_vector",
            param={"metric_type": "COSINE", "params": {"nprobe": 10}},
            limit=c
        )
        # 创建稀疏向量搜索请求
        sparse_request = AnnSearchRequest(
            data=[sparse_query_vector],
            anns_field="sparse_vector",
            param={"metric_type": "IP", "params": {"nprobe": 5}},
            limit=c
        )

        # 创建加权排序器，稀疏向量权重 0.7，稠密向量权重 1.0
        ranker = WeightedRanker(configs.SPARSE_WEIGHT, configs.DENSE_WEIGHT)
        # 执行混合搜索，返回 k结果
        results = self.client.hybrid_search(
            collection_name=self.collection_name,# 集合名称
            reqs=[dense_request, sparse_request],# 混合搜索请求
            ranker=ranker,# 加权排序实例
            limit=configs.k,# 返回的Top-K
            output_fields=["parent_content"]# 在返回字段里添加parent_content关联父文档内容
        )
        # 从子块中提取去重的父文档
        # 先用set去重 然后回复成列表
        results = list(set([result["parent_content"] for result in results]))
        return results

    def rerank(self,query,results,m=configs.CANDIDATE_M):
        return self.rerank_model.rerank(query,results)[:m]

    # 定义方法，执行混合检索并重排序
    def hybrid_search_with_rerank(self, query, k=configs.RETRIEVAL_K, m =configs.CANDIDATE_M):
        results = self.hybrid_search(query, k)
        return self.rerank(query, results, m)

if __name__ == '__main__':
    vs = VectorStore()
    # a = vs.hybrid_search_with_rerank("如何使用Langchain")
    # print(a)