from conn import redis_conn

R = redis_conn.RedisClient()
ttl = 86400 # 24小时

class QuestionCache:

    @staticmethod
    def insert_questions(questions):
        R.client.lpush("questions", *questions)
        R.expire("questions", ttl)

    @staticmethod
    def get_question_by_index(id):
        return R.client.lindex("questions", id)

    @staticmethod
    def get_all_questions():
        return R.client.lrange("questions", 0, -1)

class AnswerCache:

    @staticmethod
    def set_answer(query, answer):
        R.client.set(f"answer:{query}", answer,ex=ttl)

    @staticmethod
    def get_answer(query):
        return R.client.get(f"answer:{query}")



