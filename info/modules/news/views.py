# from flask import session
from flask import render_template, current_app
# 导入蓝图对象，使用蓝图创建路由映射
from . import news_blue


@news_blue.route('/')
def index():
    # session['authen'] = 'id'
    return render_template('news/index.html')


@news_blue.route('/favicon.ico')
def favicon():
    # 把favicon图标传给浏览器，发送静态文件给浏览器
    return current_app.send_static_file('news/favicon.ico')
