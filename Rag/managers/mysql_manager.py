
from conn import mysql_conn as MC
import datetime
from uuid import uuid4

mc = MC.MysqlConn()


class QuestionManager:

    @staticmethod
    def get_all_questions():
        resutls = mc.searh_all("jpkb",["question"])
        return [result['question'] for result in resutls]
    @staticmethod
    def get_anwear_by_question(question):
        sql = 'select answer from jpkb where question =%s'
        params = (question,)
        results = mc.search_with_params(sql, params)
        return results[0]['answer'] if results else None
class MemeryManager:

    # 插入会话记录
    @staticmethod
    def insert_memery(question,answer,session_id):
        d = {'question':question,'answer':answer,'session_id':session_id,'create_time':datetime.datetime.now(),'state':1}
        mc.insert('conversation',d)


    # 仅返回一个会话id
    @staticmethod
    def new_session():
        return str(uuid4())

    # 根据session_id得到前k个聊天历史并拼接一下返回
    @staticmethod
    def search_history(session_id,k=3):
        sql = 'select question,answer from conversation where session_id =%s and state=1 order by create_time desc limit %s'
        params = (session_id,k)
        historys = mc.search_with_params(sql, params)
        s = ''
        for history in historys:
            s += f"问题:{history['question']}。回答：{history['answer']}\n"
        return s

    # 根据session_id清空会话记录,将状态改为0
    @staticmethod
    def clear_memery(session_id):
        sql = 'update conversation set state=0 where se  ="%s"' % session_id
        mc.execute(sql)



if __name__ == '__main__':
    import time
    #模拟一下memery
    session_id = '123'
    # for i in range(5):
    #     MemeryManager.insert_memery('问题%s'%i,'答案%s'%i,session_id)
    #     time.sleep(1)
    #     print(i)
    print(MemeryManager.search_history(session_id))
    MemeryManager.clear_memery("a2451a79-fc54-4f94-bd88-e3f5150a4faa")