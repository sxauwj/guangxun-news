from flask import render_template, current_app
# 导入蓝图对象，使用蓝图创建路由映射
from . import news_blue
# 导入flask内置的对象
from flask import session
# 导入模型类
from info.models import User

@news_blue.route('/')
def index():
    """
    首页：
    实现页面右上角，检查用户登录状态，如果用户登录，显示用户信息，如果未登录，提供登录注册入口
    1.从redis中获取用户id
    2.根据user_id查询mysql，获取用户信息
    3.把用户信息，传给模板
    :return:
    """
    user_id = session.get('user_id')
    print(user_id)
    user = None
    # 根据user_id 读取mysql，获取用户信息
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
    data = {
        # 三元运算　如果user存在则user_info有值否则为None
        'user_info':user.to_dict() if user else None
    }
    return render_template('news/index.html',data=data)


@news_blue.route('/favicon.ico')
def favicon():
    # 把favicon图标传给浏览器，发送静态文件给浏览器
    return current_app.send_static_file('news/favicon.ico')
