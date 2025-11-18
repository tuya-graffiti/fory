from rank_bm25 import BM25Okapi
import numpy as np
import jieba
from managers import mysql_manager as mm #,redis_manager as rm
from utils.general_utils.time_util import timer

class BM25Search:
    def __init__(self):
        self.bm25 = self._init_bm25()
    def _init_bm25(self):
        # 从Redis中获取所有问题
        # questions = rm.QuestionCache.get_all_questions()
        questions = False
        # 如果Redis中没有问题query，则从mysql数据库中加载数据
        if not questions:
            questions = mm.QuestionManager.get_all_questions()
        tokenized_questions = [jieba.lcut(q) for q in questions]
        # 存储原始问题到Redis 略
        # 初始化BM25模型
        return BM25Okapi(tokenized_questions)
    def _softmax(self,scores):
        exp_scores = np.exp(scores - np.max(scores))
        return exp_scores/exp_scores.sum()
    def _bm_search(self,query):
        scores = self.bm25.get_scores(jieba.lcut(query.lower()))
        softmax_scores = self._softmax(scores)
        best_idx = int(softmax_scores.argmax())
        best_score = softmax_scores[best_idx]
        return best_idx,best_score
    @timer
    def search(self,query,thresold=0.85):
        # 这里转的很奇怪 回溯？ 改代码时看原代码 同时存在query和question
        # cached_answer = rm.AnswerCache.get_answer(query)
        # if cached_answer:
        #     return cached_answer
        best_idx,best_score = self._bm_search(query)
        if best_score >= thresold:
            answer = mm.QuestionManager.get_anwear_by_question(query)
            return answer
        else:
            return None
if __name__ == '__main__':
    bs = BM25Search()
    query = "请问可以帮我,看看简历可以吗?"
    # query = "为什么第三天和第九天生成jwt的方式不一样"
    a = bs.search(query)
    print(a)


