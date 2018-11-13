# 导入蓝图
from flask import Blueprint

# 创建蓝图对象
news_blue = Blueprint('news_blue', __name__)

# 把使用蓝图对象的文件，导入到创建蓝图对象的下面
from . import views
