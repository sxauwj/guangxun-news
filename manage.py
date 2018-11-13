# 集成管理脚本
from flask import session
from flask_script import Manager
from info import create_app

# 调用函数，获取app，传入参数，通过参数的不同，可以获取不同环境下的app
app = create_app('development')

# 使用管理器对象,将管理器关联app
manage = Manager(app)

if __name__ == '__main__':
    manage.run()
