from flask import g,redirect,render_template,request,jsonify,current_app,session
from . import profile_blue
# 导入登录验证装饰器
from info.utils.commons import  login_required
from info.utils.response_code import RET
from info import db


@profile_blue.route('/info')
@login_required
def user_info():
    """
    用户登录信息显示
    １尝试获取用户信息
    ２如果用户未登录，重定向到项目首页
    ３如果用户已登录，使用模板渲染用户数据
    :return:
    """
    user = g.user
    if not user:
        return redirect('/')
    data = {
        'user':user.to_dict()
    }
    return render_template('news/user.html',data=data)
@profile_blue.route('/base_info',methods=['GET','POST'])
@login_required
def base_info():
    """
    用户基本信息
    1.如果用户，请求方法为get的情况下，使用模板渲染用户数据
    2.如果是post请求，获取参数nick_name,signature,gender(MAN/WOMAN)
    3.检查参数的完整性
    4.检查性别参数在范围内
    5.保存用户信息
    6.提交数据
    7.返回结果

    :return:
    """
    user =g.user
    # 判断如果是get请求，渲染模板
    if request.method == 'GET':
        data = {
            'user':user.to_dict()
        }
        return render_template('news/user_base_info.html',data=data)
    # 获取参数
    nick_name = request.json.get('nick_name')
    signature = request.json.get('signature')
    gender = request.json.get('gender')
    #　检查参数
    if not all([nick_name,signature,gender]):
        return jsonify(errno=RET.PARAMERR,errmsg='参数缺失')
    # 检查性别参数在范围内
    if gender not in ['MAN','WOMAN']:
        return jsonify(errno=RET.PARAMERR,errmsg='非法参数')
    # 保存用户信息
    user.nick_name = nick_name
    user.signature = signature
    user.gender = gender
    # 提交数据
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR,errmsg='保存数据失败')
    # 需要修改redis缓存中的昵称
    session['nick_name'] = user.nick_name
    # 返回结果
    return jsonify(errno=RET.OK,errmsg='OK')

