from info.models import User
from info.utils.commons import login_required
from . import admin_blue
from flask import render_template, request, g, session, redirect, url_for, current_app


@admin_blue.route('/index')
@login_required
def index():
    """后台管理首页"""
    user = g.user
    return render_template('admin/index.html', user=user.to_dict())


@admin_blue.route('/login', methods=['GET', 'POST'])
def login():
    """
    后台管理员登录
    1.如果为get请求，使用session获取登录信息，user_id,is_admin
        2.判断用户 如果用户id存在并是管理员，重定向到后台管理页面
            3.获取参数，user_name,password
                4.校验参数的完整性
                    5.查询数据库，确认用户存在，is_admin为true,校验密码
                        6.缓存用户信息，user_id,mobile,nick_name,is_admin
                            7.跳转到后台管理页面
    :return:
    """
    if request.method == 'GET':
        user_id = session.get('user_id', None)
        is_admin = session.get('is_admin', False)
        if user_id and is_admin:
            return redirect(url_for('admin.index'))
        return render_template('admin/login.html')
    # 获取参数
    username = request.form.get('username')
    password = request.form.get('password')
    # 检查参数完整性
    if not all([username, password]):
        return render_template('admin/login.html', errmsg='参数缺失')
    try:
        user = User.query.filter(User.mobile == username).first()
    except Exception as e:
        current_app.logger.error(e)
        return render_template('admin/login.html', errmsg='数据查询失败')
    if not user or not user.check_password(password):
        return render_template('admin/login.html', errmsg='帐号或密码错误')
    if not user.is_admin:
        return render_template('admin/login.html', errmsg='用户权限错误')
    session['user_id'] = user.id
    session['nick_name'] = user.nick_name
    session['mobile'] = user.mobile
    # 状态保持，可以进入除后台登录界面的其他后台页面
    session['is_admin'] = True
    #  跳转页面
    return redirect(url_for('admin.index'))
