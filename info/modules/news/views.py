from flask import render_template, current_app, jsonify, request, g
# 导入蓝图对象，使用蓝图创建路由映射
from . import news_blue
# 导入flask内置的对象
from flask import session
# 导入模型类
from info.models import News, Category, Comment
# 导入常量文件
from info import constants, db
# 导入响应状态码
from info.utils.response_code import RET
# 导入登录验证装饰器
from info.utils.commons import login_required


@news_blue.route('/')
@login_required
def index():
    """
    一.首页：
    实现页面右上角，检查用户登录状态，如果用户登录，显示用户信息，如果未登录，提供登录注册入口
    1.从redis中获取用户id
    2.根据user_id查询mysql，获取用户信息
    3.把用户信息，传给模板
    二. 新闻点击排行展示
    根据新闻点击次数查询数据库，使用模板渲染数据

    :return:
    """
    # user_id = session.get('user_id')
    #
    # user = None
    # # 根据user_id 读取mysql，获取用户信息
    # if user_id:
    #     try:
    #         user = User.query.get(user_id)
    #     except Exception as e:
    #         current_app.logger.error(e)

    # 　登录验证成功可以获得g.user
    user = g.user

    # 新闻点击排行
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询新闻排行数据失败')
    # 判断查询结果
    if not news_list:
        return jsonify(errno=RET.NODATA, errmsg='无新闻')
    # 定义容器，存储新闻数据
    news_click_list = []
    for news in news_list:
        news_click_list.append(news.to_dict())
        # print(news.todict())
    # 新闻分类展示
    try:
        categories = Category.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询数据库失败')
    # 判断查询结果
    if not categories:
        return jsonify(errno=RET.NODATA, errmsg='无新闻分类')
    # 定义容器，存储新闻分类数据
    category_list = []
    for category in categories:
        category_list.append(category.to_dict())

    data = {
        # 三元运算　如果user存在则user_info有值否则为None
        'user_info': user.to_dict() if user else None,
        'news_click_list': news_click_list,
        'category_list': category_list

    }

    return render_template('news/index.html', data=data)


@news_blue.route('/news_list')
def news_list():
    """
        首页新闻列表
        获取参数－－检查参数－－处理参数－－返回结果
        1 获取参数，get请求，　cid page per_page
            2 检查参数，转换参数数据类型，防止不正常数据
            cid,page,per_page= int(cid),int(page),int(per_page)
                3 根据分类id查询新闻列表，新闻列表默认按照新闻发布时间倒序排序
                    ４　判断用户选择的新闻分类
                        ５　获取分页后的数据
                            　paginate.items 分页总数据（对象类型）
                            　paginate.pages 分页总页数
                            　paginate.page 分页当前页数
                                ６　遍历分页后的总数据，调用模型类中的方法，转成字典
                                    ７　返回数据

    """
    # 获取参数
    cid = request.args.get('cid', '1')
    page = request.args.get('page', '1')
    per_page = request.args.get('per_page', '10')
    # 检查参数
    try:
        cid, page, per_page = int(cid), int(page), int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='参数类型错误')
    # 根据分类id查询数据库
    filters = []
    # 如果分类id不是最新即id为１，添加分类id给filters过滤条件
    if cid > 1:
        filters.append(News.category_id == cid)
    try:
        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page, per_page, False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询新闻列表失败')
    # 使用分页对象，获取分页后的数据　总数据　总页数　当前页数
    # 列表形式　存储对象
    news_list = paginate.items
    total_page = paginate.pages
    current_page = paginate.pages
    news_dict_list = []
    # 遍历分页数据，转成字典
    for news in news_list:
        news_dict_list.append(news.to_dict())
    # 定义容器
    data = {
        'total_page': total_page,
        'current_page': current_page,
        'news_dict_list': news_dict_list
    }
    # 返回数据
    return jsonify(errno=RET.OK, errmsg='OK', data=data)


@news_blue.route('/<int:news_id>')
@login_required
def news_detail(news_id):
    """
    新闻详情：
    １.根据news_id，查询mysql数据库
    ２.使用模板渲染数据
    :param news_id:
    :return:
    """

    # user_id = session.get('user_id')
    #
    # user = None
    # # 根据user_id 读取mysql，获取用户信息
    # if user_id:
    #     try:
    #         user = User.query.get(user_id)
    #     except Exception as e:
    #         current_app.logger.error(e)

    user = g.user

    # 新闻点击排行
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询新闻排行数据失败')
    # 判断查询结果
    if not news_list:
        return jsonify(errno=RET.NODATA, errmsg='无新闻')
    # 定义容器，存储新闻数据
    news_click_list = []
    for news in news_list:
        news_click_list.append(news.to_dict())

    # 查询数据库显示新闻详情
    news = None
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询新闻详情失败')
    # 判断查询结果
    if not news:
        return jsonify(errno=RET.NODATA, errmsg='无新闻数据')
    news.clicks += 1

    try:
        db.session.add(news)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='保存数据失败')

    # 定义标记，用来标识用户是否已经收藏该新闻
    is_collected = False
    # 是否显示提醒登录框
    tips = True
    # 判断用户是否登录，以及用户是否收藏该新闻
    if g.user and news in user.collection_news:
        tips = False
        is_collected = True

    # 新闻评论信息
    try:
        comment_list = Comment.query.filter(Comment.news_id == news.id).order_by(Comment.create_time.desc())
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询新闻评论失败')
    # 定义容器
    comments = []
    # 如果该新闻有评论
    if comment_list:
        for comment in comment_list:
            comments.append(comment.to_dict())

    # 定义容器，返回数据
    data = {
        'news_detail': news.to_dict(),
        # 三元运算　如果user存在则user_info有值否则为None
        'user_info': user.to_dict() if user else None,
        'news_click_list': news_click_list,
        'is_collected': is_collected,
        'tips': tips,
        'comments': comments,
        # 'auth_user':auth_user
    }

    return render_template('news/detail.html', data=data)


@news_blue.route('/news_collect', methods=['POST'])
@login_required
def user_collect():
    """
    用户收藏取消收藏
    1.判断用户是否登录
    2.如果没登录，返回错误信息
    3.获取参数，news_id, action[collect,cancel_collect]
    4.检查参数的完整性
    5.转换参数类型news_id
    6.检查action是否是［collect,cancel_collect]
    7.判断如果用户选择的是收藏，添加该新闻
    8.否则，移除用户收藏的新闻
    9.返回结果
    :return:
    """
    # 验证是否登录
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg='用户未登录')
    # 获取参数
    news_id = request.json.get('news_id')
    action = request.json.get('action')
    # 检查参数
    if not all([news_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数缺失')
    # 转换参数类型
    try:
        news_id = int(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='参数类型错误')
    # 检查action参数
    if action not in ['collect', 'cancel_collect']:
        return jsonify(errno=RET.PARAMERR, errmsg='参数格式错误')
    # 根据news_id查询新闻，确认新闻的存在
    news = None
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
    if not news:
        return jsonify(errno=RET.NODATA, errmsg='无新闻数据')
    # 如果用户是收藏
    if action == 'collect':
        # 判断用户没有收藏过
        if news not in user.collection_news:
            user.collection_news.append(news)
    else:
        user.collection_news.remove(news)
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


# 用户点赞
@news_blue.route('/comment_like', methods=['POST'])
@login_required
def news_like():
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg='用户未登录')
    # 获取参数
    comment_id = request.json.get('comment_id')
    action = request.json.get('action')
    # 检查参数
    if not all([comment_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数缺失')
    try:
        comment_id = int(comment_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='参数类型错误')
    if action not in ['add', 'remove']:
        return jsonify(errno=RET.PARAMERR, errmsg='参数格式错误')
    # 数据处理
    comment = None
    try:
        comment = Comment.query.get(comment_id)
    except Exception as e:
        current_app.logger.error(e)
    if not comment:
        return jsonify(errno=RET.NODATA, errmsg='无评论对象')
    print("点赞行为",action)

    if action == 'add':
        comment.like_count += 1
    else:
        comment.like_count -= 1

    # 提交数据
    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='保存数据失败')

    # 返回响应
    return jsonify(errno=RET.OK, errmsg='OK')


@news_blue.route('/news_comment', methods=['POST'])
@login_required
def news_comments():
    """
    新闻评论
    获取参数－－检查参数－－处理参数－－返回结果
    1.用户必要登录
    2.检查参数　news_id , comment, parent_id(可选)
    3.转换参数的数据类型，判断parent_id是否存在
    4．查询新闻，确认新闻的存在
    5.保存评论信息，判断parent_id是否存在
    6.提交数据
    7.返回结果
    :return:
    """
    # 判断用户是否已经登录
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg='用户未登录')

    # 获取参数
    news_id = request.json.get('news_id')
    content = request.json.get('comment')
    parent_id = request.json.get('parent_id')

    # 检查参数
    if not all([news_id, content]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数缺失')
    # 转换类型，防止获得不合法数据，增加程序的健壮性
    try:
        news_id = int(news_id)
        # 如果有父评论
        if parent_id:
            parent_id = int(parent_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='参数类型错误')
    # 查询数据库，确认新闻存在
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询新闻失败')
    # 判断查询结果
    if not news:
        return jsonify(errno=RET.NODATA, errmsg='无新闻数据')
    # 构造评论的模型对象
    comment = Comment()
    comment.user_id = user.id
    comment.news_id = news.id
    comment.content = content
    # 如果父评论存在，保存父评论信息
    if parent_id:
        comment.parent_id = parent_id
    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='保存评论失败')
    # 返回结果
    return jsonify(errno=RET.OK, errmsg='OK', data=comment.to_dict())


@news_blue.route('/favicon.ico')
def favicon():
    # 把favicon图标传给浏览器，发送静态文件给浏览器
    return current_app.send_static_file('news/favicon.ico')
