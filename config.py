# 导入创建redis实例的StrictRedis
from redis import StrictRedis
# 集成python的标准日志模块
import logging


class Config:
    DEBUG = None
    LOG_LEVEL = logging.DEBUG
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@localhost/guangxun'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 实现状态保持,配置session信息存储在redis中
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379
    SESSION_TYPE = 'redis'
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    # 设置session 有效期的设置，该属性是Flask内置的session有效期
    PERMANENT_SESSION_LIFITIME = 86400
    # 设置session密钥
    SECRET_KEY = 'oTTnEzkP+a6pIzgcSnOiOCf9a8TYfCEPQ7E4qQLCOv0pp/PrnjF44g8Z5tts'

# 封装不同环境下的配置类
# 开发模式
class Development(Config):
    DEBUG = True

# 生产模式
class Production(Config):
    DEBUG = False
    LOG_LEVEL = logging.ERROR

# 定义字典，实现不同环境下的配置类的映射
class_dict ={
    'development': Development,
    'production': Production,

}