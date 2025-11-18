from sentence_transformers import CrossEncoder
import torch
from datas import filepaths
import os
device = "cuda" if torch.cuda.is_available() else "cpu"


class RerankModel():
    def __init__(self, device=device):
        model_path = os.path.join(filepaths.MODELS_DIR, 'bge-reranker-base') # rerank模型地址
        self.model = CrossEncoder(model_path, device=device)

    def rerank(self, query, docs):
        pairs = [[query, doc] for doc in docs]
        # 使用 BGE-Reranker 计算每个配对的得分
        scores = self.model.predict(pairs)
        # 根据得分从高到低排序文档
        ranked_docs = [doc for score, doc in sorted(zip(scores, docs), reverse=True)]
        return ranked_docs


if __name__ == '__main__':
    model = RerankModel()
    queries = '样例文档-2'
    passages = ["样例文档-1", "样例文档-2"]
    docs = model.rerank(queries, passages)
    print(docs)

