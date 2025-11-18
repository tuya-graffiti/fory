# 导入 Redis 客户端
import redis
from base import config_gen as cfg

class RedisClient:
    def __init__(self):
        self.client = redis.Redis(
            host=cfg.REDIS.HOST,
            port=cfg.REDIS.PORT,
            password=cfg.REDIS.PASSWORD,
            db=cfg.REDIS.DB,
            decode_responses=True
        )

    # 设置过期时间
    def expire(self, key, ex):
        """
        :param key: key名
        :param ex: 过期时间（秒）
        :return: True/False 成功或失败
        """
        return self.client.expire(key, ex)


if __name__ == '__main__':
    r = RedisClient()
    # 随便ping一下
    print(r.client.ping())