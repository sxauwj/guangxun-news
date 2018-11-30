# 集成管理脚本
from flask_script import Manager
# 数据库迁移的扩展
from flask_migrate import Migrate, MigrateCommand
# 导入info目录下的create_app
from info import create_app, db, models
# 导入创建管理员的模型类
from info.models import User
# 调用函数，获取app，传入参数，通过参数的不同，可以获取不同环境下的app
app = create_app('development')

# 使用管理器对象,将管理器关联app
manage = Manager(app)
# 使用迁移框架
Migrate(app, db)
manage.add_command('db', MigrateCommand)

# 创建管理员账户
# 在script扩展中，自定义脚本命令，以自定义函数的形式实现创建管理员用户
# 以终端启动命令的形式实现
# 在终端中使用命令：python manage.py create_supperuser -n admin -p 123456
@manage.option('-n','-name', dest='name')
@manage.option('-p','-password',dest='password')
def create_supperuser(name, password):
    if not all([name, password]):
        print('参数缺失')
    user = User()
    user.nick_name = name
    user.mobile = name
    user.password = password
    user.is_admin = True
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)
    print('管理员创建成功')



if __name__ == '__main__':
    # print(app.url_map)
    manage.run()
