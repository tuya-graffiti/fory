from online.mysql_search.bm25_search import BM25Search
from online.rag_system.rag_system import RAGSystem
from managers.mysql_manager import MemeryManager
from utils.general_utils.time_util import timer

history_k = 3
show_history_k = 10
class EduQASystem:
    @timer
    def __init__(self):
        self.bm25 = BM25Search()
        self.rag = RAGSystem()
        self.memory = MemeryManager()
    @timer
    def get_answer(self,query,session_id):
        answer = self.bm25.search(query)
        if answer:
            return answer
        else:
            history = self.memory.search_history(session_id,history_k)
            def streaming_with_memory():
                answer_content = ''
                for chunk in self.rag.generate_answer(query,history):
                    answer_content += chunk
                    yield chunk
                self.memory.insert_memery(query,answer_content,session_id)
            return streaming_with_memory()

    def clear_session(self, session_id):
        self.memery.clear_memery(session_id)
    def new_session(self):
        session_id = self.memery.new_session()
        return session_id

    # 切换会话
    def switch_session(self, session_id):
        history = self.memery.search_history(session_id, show_history_k)
        return history
if __name__ == '__main__':
    from utils.general_utils.globle_util import stream_print
    system = EduQASystem()
    session_id = 'aa11'
    while True:
        query = input('请输入问题')
        if query == 'exit':
            break
        res = system.get_answer(query,session_id)
        stream_print(res)
        print('\n')