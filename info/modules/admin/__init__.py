from flask import Blueprint, session, request, url_for, redirect

admin_blue = Blueprint('admin', __name__, url_prefix='/admin')
from . import views


# 权限校验，作用：是让普通用户无法访问除login页面外的其他后台页面
# 当执行admin_blue下的路由前先执行该校验
@admin_blue.before_request
def check_admin():
    # 如果不是管理员，那么直接跳转到主页
    is_admin = session.get('is_admin', False)
    # 如果不是管理员，并且当前访问的url不是后台登录页面
    # request.url.endswith('/admin/login')
    if not is_admin and not request.url.endswith(url_for('admin.login')):
        return redirect('/')
