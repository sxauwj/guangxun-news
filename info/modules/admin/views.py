from info.models import User
from info.utils.commons import login_required
from . import admin_blue
from flask import render_template, request, g, session, jsonify, redirect, url_for, current_app
from info.utils.response_code import RET
# 导入时间模块，用来获取日期时间的字符串
import time
# 导入日期模块
from datetime import datetime, timedelta


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


@admin_blue.route('/user_count')
def user_count():
    """
    后台管理，用户统计
    1.总人数，非管理员的所有注册用户
    2.月新增人数，非管理员的所有注册用户，并且是每月1日0时0分0秒时间后注册的用户
    3.日新增人数，非管理员的所有注册用户，并且是每天0时0分0秒后注册的用户
    :return:
    """
    # 总人数
    total_count = 0
    # 查询mysql,获取所有非管理员的人数
    try:
        total_count = User.query.filter(User.is_admin == False).count()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询总人数失败')

    # 月新增人数，非管理员的所有注册用户，并且是每月1日0时0分0秒时间后注册的用户
    # 比较时间：用户的注册时间大于每月1日的时间
    mon_count = 0
    # 实例化时间对象
    # tm_year= , tm_mon= , tm_mday=
    t = time.localtime()
    # 拼接字符串，获取每月的1号日期字符串
    mon_start_date_str = '%d-%02d-01' % (t.tm_year, t.tm_mon)
    # 把日期字符串对象转换成日期对象，年%Y月%m日%d
    mon_start_date = datetime.strptime(mon_start_date_str, '%Y-%m-%d')
    # 根据日期对象，来查询用户的月新增人数
    try:
        mon_count = User.query.filter(User.is_admin == False, User.create_time > mon_start_date).count()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询月新增人数失败')

    # 日新增人数
    day_count = 0
    today_date_str = '%d-%02d-%02d' % (t.tm_year, t.tm_mon, t.tm_mday)
    today_date = datetime.strptime(today_date_str, '%Y-%m-%d')
    # 根据日期对象，来查询用户的日新增人数
    try:
        day_count = User.query.filter(User.is_admin == False, User.create_time > today_date).count()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询日新增人数失败')
    #####
    # 统计用户活跃度
    active_count = []
    active_time = []
    # 生成当前日期的字符串
    current_date_str = '%d-%02d-%02d' % (t.tm_year, t.tm_mon, t.tm_mday)
    # 转换成日期对象
    current_date = datetime.strptime(current_date_str, '%Y-%m-%d')
    # 让日期往前推30天，current_date-timedelta()
    # 获取每天的开始时间(当天的0时0分0秒)和结束时间(第二天的0时0分0秒)
    for d in range(31):
        # 每天开始的时间
        begin_date = current_date - timedelta(days=d)
        end_date = current_date - timedelta(days=(d - 1))
        # 根据时间查询数据库
        try:
            count = User.query.filter(User.is_admin == False, User.last_login >= begin_date,
                                      User.last_login < end_date).count()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg='查询活跃用户人数失败')
        # 把统计结果添加到列表中
        active_count.append(count)
        # 把日期对象转换成字符串
        begin_date_str = datetime.strftime(begin_date, '%Y-%m-%d')
        active_time.append(begin_date_str)
        print(active_time)

    active_time.reverse()
    active_count.reverse()

    data = {
        'total_count': total_count,
        'mon_count': mon_count,
        'day_count': day_count,
        'active_count': active_count,
        'active_time': active_time
    }

    return render_template('admin/user_count.html', data=data)
