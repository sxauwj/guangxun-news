from flask import g, redirect, render_template, request, jsonify, current_app, session
from . import profile_blue
# 导入登录验证装饰器
from info.utils.commons import login_required
from info.utils.response_code import RET
from info.utils.image_storage import storage
from info import constants
from info import db
# 导入模型类
from info.models import Category, News


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
        'user': user.to_dict()
    }
    return render_template('news/user.html', data=data)


@profile_blue.route('/base_info', methods=['GET', 'POST'])
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
    user = g.user
    # 判断如果是get请求，渲染模板
    if request.method == 'GET':
        data = {
            'user': user.to_dict()
        }
        return render_template('news/user_base_info.html', data=data)
    # 获取参数
    nick_name = request.json.get('nick_name')
    signature = request.json.get('signature')
    gender = request.json.get('gender')
    # 　检查参数
    if not all([nick_name, signature, gender]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数缺失')
    # 检查性别参数在范围内
    if gender not in ['MAN', 'WOMAN']:
        return jsonify(errno=RET.PARAMERR, errmsg='非法参数')
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
        return jsonify(errno=RET.DBERR, errmsg='保存数据失败')
    # 需要修改redis缓存中的昵称
    session['nick_name'] = user.nick_name
    # 返回结果
    return jsonify(errno=RET.OK, errmsg='OK')


@profile_blue.route('/pic_info', methods=['GET', 'POST'])
@login_required
def save_avatar():
    """
    保存头像
    1.判断用户是否登录，如果登录，判断请求方法，使用模板渲染数据
        2.如果不是get请求，获取参数，avatar，文件对象（具有read和wirte方法的对象）
        request.files.get('avatar')
            3.读取图片数据
                4.调用七牛云上传图片，保存图片名称
                    5.再mysql数据库中，存储图片的链接
                        6.提交数据
                            7.返回图片链接给前端

    :return:
    """
    user = g.user
    if request.method == 'GET':
        data = {
            'user': user.to_dict()
        }
        return render_template('news/user_pic_info.html', data=data)
    # 获取参数
    avatar = request.files.get('avatar')
    # 检查参数存在
    if not avatar:
        return jsonify(errno=RET.PARAMERR, errmsg='参数缺失')
    # 读取图片数据
    try:
        image_data = avatar.read()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='参数格式错误')
    # 调用七牛云，返回图片的名称
    try:
        image_name = storage(image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg='上传图片失败')
    # 保存图片数据
    user.avatar_url = image_name
    # 提交数据到mysql中
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='保存数据失败')
    # 拼接图片的绝对路径：七牛云的空间域名　+ 七牛云返回的图片名称
    avatar_url = constants.QINIU_DOMIN_PREFIX + image_name
    # 返回结果
    data = {
        'avatar_url': avatar_url
    }
    return jsonify(errno=RET.OK, errmsg='OK', data=data)


@profile_blue.route('/news_release', methods=['GET', 'POST'])
@login_required
def news_release():
    """
    新闻发布
    1.获取用户信息，如果是get请求，查询新闻分类信息，移除最新分类，传给模板
    2.获取参数，title category_id digest index_image,content
    3.检查参数的完整性
    4.转换分类id的数据类型
    5.读取数据内容，调用七牛云上传新闻图片
    6.构造模型类对象，保存新闻数据
    7.返回结果
    :return:
    """
    user = g.user
    if request.method == 'GET':
        # 查询新闻分类，查询出不是最新的所有分类
        try:
            categories = Category.query.all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg='查询数据失败')
        # 判断查询结果
        if not categories:
            return jsonify(errno=RET.NODATA, errmsg='无新闻分类信息')
        # 定义容器存储新闻分类数据
        category_list = []
        for category in categories:
            category_list.append(category.to_dict())
        # 移除索引为０的新闻分类（最新)
        category_list.pop(0)
        # 定义字典
        data = {
            'categories': category_list
        }
        return render_template('news/user_news_release.html', data=data)
    # 用户提交数据，获取参数:title category_id,digest,index_image,content
    title = request.form.get('title')
    category_id = request.form.get('category_id')
    digest = request.form.get('digest')
    index_image = request.files.get('index_image')
    content = request.form.get('content')
    print(title, category_id, digest, index_image, content)
    # 检查参数的完整性
    if not all([title, category_id, digest, index_image, content]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数缺失')
    # 转换参数类型
    try:
        category_id = int(category_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='参数类型错误')
    # 读取图片数据
    try:
        image_data = index_image.read()
    except Exception  as e:
        current_app.logger.errnor(e)
        return jsonify(errno=RET.PARAMERR, errmsg='参数格式错误')
    # 上传封面图片
    try:
        image_name = storage(image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg='上传图片失败')
    # 保存新闻数据
    news = News()
    news.title = title
    news.category_id = category_id
    news.digest = digest
    news.index_image_url = constants.QINIU_DOMIN_PREFIX + image_name
    news.content = content
    news.user_id = user.id
    news.source = '个人发布'
    news.status = 1
    # 提交数据
    try:
        db.session.add(news)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='保存数据失败')
    # 返回结果
    return jsonify(errno=RET.OK, errmsg='OK')

@profile_blue.route('/todo_news_list')
@login_required
def news_list():
    data = '<h1>news_list<h1>'
    # return render_template('news/user_news_list2.html',data=data)
    return data