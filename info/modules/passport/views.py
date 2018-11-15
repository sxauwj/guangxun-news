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
# 导入正则
import re,random
# 导入云通讯
from info.libs.yuntongxun.sms import CCP


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

@passport_blue.route('/sms_code', methods=['POST'])
def send_sms_code():
    """
    发送短信
    接受参数－－检查参数－－业务处理－－返回结果
    １.获取参数，手机号mobile,验证码内容image_code,验证码编号image_code_id
    2.检查参数，参数必须全部存在
    3.检查手机号的格式，使用正则
    4.检查图片验证码是否正确
        5.从redis中获取真实的图片验证码　（可能超时不存在了）
            6.判断获取结果是否存在
                7.如果存在，先删除redis数据库中的图片验证码，因为图片验证码只能比较一次，比较一次的本质，是只能读取redis数据库一次
                8.比较图片验证码是否正确
                9.生成短信验证码６位数
                10.把短信验证码存储在redis数据库中
                11.调用云通讯发送短信
                12.保存发送结果（000000），用来判断发送是否成功
                13.返回结果
    :return:
    """
    # 获取post请求的参数
    mobile = request.json.get('mobile')
    image_code = request.json.get('image_code')
    image_code_id  = request.json.get('image_code_id')
    # 检查参数完整性
    if not all([mobile, image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR,errmsg='参数缺失')
    # 检查手机号格式
    if not re.match(r'1[3456789]\d{9}$',mobile):
        return jsonify(errno=RET.PARAMERR,errmsg='手机号格式错误')
    # 根据uuid从redis中获取图片验证码
    try:
        real_image_code = redis_store.get('ImageCode_' + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='查询数据失败')
    # 判断获取结果
    if not real_image_code:
        return jsonify(errno=RET.NODATA,errmsg='图片验证码已经过期')
    # 如果获取到了图片验证码，需要把redis中的图片验证码删除，因为只能get一次
    try:
        redis_store.delete('ImageCode_' + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
    # 比较图片验证码是否正确
        if real_image_code.lower() != image_code.lower():
            return jsonify(errno=RET.DATAERR,errmsg='图片验证码错误 ')

    # 生成短信随机码
    sms_code = '%06d' % random.randint(0,999999)
    # 存入redis中
    try:
        redis_store.setex('SMSCode_' + mobile,constants.SMS_CODE_REDIS_EXPIRES,sms_code)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存数据失败')
    # 调用云通讯发送短信
    try:
        # 构造发送短信对象
        ccp = CCP()
        # 第一个参数是手机号，第二个参数是短信内容，第三个参数是模板ｉｄ
        result = ccp.send_template_sms(mobile,[sms_code,constants.SMS_CODE_REDIS_EXPIRES/60],1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg='发送短信异常')
    # 判断发送结果
    if result == 0:
        return jsonify(errno=RET.OK,errmsg='发送成功')
    else:
        return jsonify(errno=RET.THIRDERR, errmsg='发送失败')








