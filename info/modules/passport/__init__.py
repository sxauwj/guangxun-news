# 导入蓝图对象
from flask import Blueprint

# 创建蓝图对象
passport_blue = Blueprint('passport_blue', __name__)

from . import views