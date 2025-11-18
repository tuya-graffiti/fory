from base import configs as cfg
from managers import vector_store as vs
from conn.llms import get_deepseek
from langchain_core.output_parsers import StrOutputParser
from utils.general_utils.time_util import timer
from online.rag_system.prompts import RAGPrompts
# from online.rag_system.query_classifier import Classifier
# from online.rag_system.strategy_selector import QueryStrategy
from utils.general_utils.loggers import logger

class RAGSystem:
    @timer
    def __init__(self):
        # 向量数据库
        self.vector_store = vs.VectorStore()
        # 设置chain
        llm = get_deepseek()
        parser = StrOutputParser()
        self.rag_chain = RAGPrompts.rag_prompt()|llm|parser
        self.general_chain = RAGPrompts.general_prompt()|llm|parser
        # 检索策略
        # self.qs = QueryStrategy()
        # self.query_classifier = Classifier()
    # 获取检索到的文档
    def _get_context(self,query):
        # 获取上下文milvus数据库?
        # new_query = self.qs.get_new_query(query)
        logger.info(f"query:{query}")
        # 子查询检索 略
        context_docs = self.vector_store.hybrid_search(query)# 略了一个重排序 直接用了hybridsearch
        return context_docs
    @timer
    def _rag_query(self,query,history):
        contexts = self._get_context(query)
        context = '\n\n'.join(contexts)
        input = {
            "context":context,
            "question":query,
            "phone":cfg.CUSTOMER_SERVICE_PHONE,
            "history":history
        }
        return self.rag_chain.stream(input)
    @timer
    def generate_answer(self,query,history=''):
        # 生成答案这里跳了 一截
        return self.general_chain.stream({"query":query,"history":history})
    # 完整输出 方便评估
    def _rag_query_evaluation(self,query,history=''):
        contexts = self._get_context(query)
        context = '\n\n'.join(contexts)
        input = {
            "context":context,
            "question" : query,
            "phone" : cfg.CUSTOMER_SERVICE_PHONE,
            "history":history
        }
        return self.rag_chain.invoke(input),context
    def for_evaluation(self,query,history=''):
        # 这里集成了一下 前面略了故直接返回
        return self._rag_query_for_evaluation(query,history)
if __name__ == '__main__':
    rag_system = RAGSystem()
    answer = rag_system.generate_answer(query = "langchain是什么")

    for chunk in answer:
        print(chunk,end="",flush = True)
