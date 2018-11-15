# 导入蓝图
from . import  passport_blue
# 导入captcha工具，生成图片验证码
from info.utils.captcha.captcha import captcha
# 导入flask内置对象
from flask import request,jsonify,current_app,make_response
# 导入自定义状态码
from info.utils.response_code import RET
# 导入redis实例
from info import redis_store
# 导入常量
from info import constants



@passport_blue.route('/image_code')
def generate_image_code():
    """
生成图片验证码
接受参数－－检查参数－－业务处理－－返回结果
参数：前端传入uuid
１．获取前端传入的uuid，查询字符串args
２．如果没有uuid返回相应的提示信息
３．调用captcha工具，生成图片验证码
    captcha 返回name.text.image三个值
４．把图片验证码的内容text，根据uuid来存入redis数据库中
５．返回图片
:return:
"""
    # 获取参数
    image_code_id = request.args.get('image_code_id')
    # 检查参数是否存在，导入response_code.py文件
    if not image_code_id:
        return jsonify(errno=RET.PARAMERR,errmsg='参数错误')
    # 存在则调用工具captcha生成图片验证码
    name,text,image = captcha.generate_captcha()
    # 把text存入redis数据库中再info/__init__文件中实例化redis对象
    try:
        redis_store.setex('ImageCode_' + image_code_id,constants.IMAGE_CODE_REDIS_EXPIRES,text)
    except Exception as e:
        # 把错误信息记录到项目日志中
        current_app.logger.error(e)
        # 直接终止程序运行
        return jsonify(errno=RET.DBERR, errmsg='存储数据失败')
    else:
        # 没有异常返回图片，但image是路径，需要通过make_response返回
        response = make_response(image)
        # 修改响应的类型
        response.headers['Content-Type'] = 'image/jpg'
        # 返回响应
        return response



