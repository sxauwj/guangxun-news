from flask import session
# 导入蓝图对象，使用蓝图创建路由映射
from . import news_blue


@news_blue.route('/')
def index():
    session['authen'] = 'id'
    return 'index'
