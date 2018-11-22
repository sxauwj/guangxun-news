# 集成管理脚本
from flask_script import Manager
# 数据库迁移的扩展
from flask_migrate import Migrate, MigrateCommand
# 导入info目录下的create_app
from info import create_app, db, models

# 调用函数，获取app，传入参数，通过参数的不同，可以获取不同环境下的app
app = create_app('development')

# 使用管理器对象,将管理器关联app
manage = Manager(app)
# 使用迁移框架
Migrate(app, db)
manage.add_command('db', MigrateCommand)

if __name__ == '__main__':
    # print(app.url_map)
    manage.run()
