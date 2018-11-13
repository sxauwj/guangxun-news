# 导入Flask类、session
from flask import Flask, session
# 集成sqlalchemy扩展
from flask_sqlalchemy import SQLAlchemy
# 集成状态保持扩展
from flask_session import Session
# 导入class_dict字典
from config import class_dict

# 创建sqlalchemy对象
db = SQLAlchemy()

def create_app(config_name):
    # 创建Flask实例app
    app = Flask(__name__)
    # app的配置信息
    app.config.from_object(class_dict['Development'])

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