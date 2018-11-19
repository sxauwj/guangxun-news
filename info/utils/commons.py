from flask import current_app,g,session

from info.models import User


def index_filter(index):
    if index == 1:
        return 'first'
    elif index ==2:
        return 'second'
    elif index ==3:
        return 'third'
    else:
        return ''

# 登录验证装饰器 添加装饰器，默认会改变函数的名字即f.__name__

#  标准模块，让被装饰的函数的属性不发生变化　等同# wrapper.__name__ = f.__name__
import functools

def login_required(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        user_id = session.get('user_id')
        user = None
        # 根据user_id 读取mysql，获取用户信息
        if user_id:
            try:
                user = User.query.get(user_id)
            except Exception as e:
                current_app.logger.error(e)
        # flask 内置的g对象，和request和session一样，在请求过程中存在,请求结束后会被销毁
        # 用来临时存储数据
        g.user = user
        # 前端调用接口，要将结果返回出去
        return f(*args, **kwargs)
    # wrapper.__name__ = f.__name__
    return wrapper