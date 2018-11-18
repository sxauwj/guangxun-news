from flask import render_template, current_app,jsonify,request,g
# 导入蓝图对象，使用蓝图创建路由映射
from . import news_blue
# 导入flask内置的对象
from flask import session
# 导入模型类
from info.models import User, News, Category
# 导入常量文件
from info import constants,db
# 导入响应状态码
from info.utils.response_code import RET

@news_blue.route('/')
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
    user_id = session.get('user_id')

    user = None
    # 根据user_id 读取mysql，获取用户信息
    if user:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)

    # 新闻点击排行
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='查询新闻排行数据失败')
    # 判断查询结果
    if not news_list:

        return jsonify(errno=RET.NODATA,errmsg='无新闻')
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
        return jsonify(errno=RET.DBERR,errmsg='查询数据库失败')
    # 判断查询结果
    if not categories:
        return jsonify(errno=RET.NODATA,errmsg='无新闻分类')
    # 定义容器，存储新闻分类数据
    category_list = []
    for category in categories:
        category_list.append(category.to_dict())
        print('category',category)
        print('category_to_dict',category.to_dict())



    data = {
        # 三元运算　如果user存在则user_info有值否则为None
        'user_info': user.to_dict() if user else None ,
        'news_click_list':news_click_list,
        'category_list':category_list

    }

    return render_template('news/index.html',data=data)


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
    cid = request.args.get('cid','1')
    page = request.args.get('page','1')
    per_page = request.args.get('per_page','10')
    # 检查参数
    try:
        cid, page, per_page = int(cid), int(page), int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR,errmsg='参数类型错误')
    # 根据分类id查询数据库
    filters = []
    # 如果分类id不是最新即id为１，添加分类id给filters过滤条件
    if cid > 1:

        filters.append(News.category_id == cid)
    try:
        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page.per_page,False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='查询新闻列表失败')
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
        'total_page':total_page,
        'current_page':current_page,
        'news_dict_list':news_dict_list
    }
    # 返回数据
    return jsonify(errno=RET.OK,errmsg='OK',data = data)


@news_blue.route('/favicon.ico')
def favicon():
    # 把favicon图标传给浏览器，发送静态文件给浏览器
    return current_app.send_static_file('news/favicon.ico')


