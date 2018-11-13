# 导入Flask类、session
from flask import Flask, session
# 集成管理脚本
from flask_script import Manager
# 集成sqlalchemy扩展
from flask_sqlalchemy import SQLAlchemy
# 导入创建redis实例的StrictRedis
from redis import StrictRedis
# 集成状态保持扩展
from flask_session import Session

# 创建Flask实例app
app = Flask(__name__)
# app的配置信息
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:mysql@localhost/guangxun'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 实现状态保持
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = StrictRedis(host='127.0.0.1', port=6379)
# 设置session 有效期的设置，该属性是Flask内置的session有效期
app.config['PERMANENT_SESSION_LIFITIME'] = 1
# 设置session密钥
app.config['SECRET_KEY'] = 'oTTnEzkP+a6pIzgcSnOiOCf9a8TYfCEPQ7E4qQLCOv0pp/PrnjF44g8Z5tts'

# 创建sqlalchemy对象，并关联app
db = SQLAlchemy(app)

# 实例化Session
Session(app)

# 使用管理器对象,将管理器关联app
manage = Manager(app)


@app.route('/')
def index():
    session['authen'] = 'id'
    return 'index'
 

if __name__ == '__main__':
    manage.run()
