# 导入Flask类、session
from flask import Flask, session
# 集成sqlalchemy扩展
from flask_sqlalchemy import SQLAlchemy
# 集成状态保持扩展
from flask_session import Session
# 导入class_dict字典
from config import class_dict
# 集成python的标准日志模块
import logging
from logging.handlers import RotatingFileHandler

# 创建sqlalchemy对象
db = SQLAlchemy()


def setup_log(config_name):
    # 设置日志的记录等级
    logging.basicConfig(level=class_dict[config_name].LOG_LEVEL)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)


def create_app(config_name):
    # 配置项目日志
    setup_log(config_name)
    # 创建Flask实例app
    app = Flask(__name__)
    # app的配置信息
    app.config.from_object(class_dict[config_name])

    # 通过db对象,让程序和db进行关联
    db.init_app(app)

    # 实例化Session
    Session(app)

    # 导入蓝图对象
    from info.modules.news import news_blue
    # 注册蓝图
    app.register_blueprint(news_blue)

    # 返回app
    return app
