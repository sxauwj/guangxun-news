from qiniu import Auth, put_data

access_key = 'SmdtGrstU8mkcHcfLIpY-C_lHIa8brda55Qz4j30'
secret_key = 'JWpOm6_E7cSgl_akYOVCSuiOs6JlqElRIaxx_JO7'

bucket_name = 'info'


def storage(data):
    try:
        q = Auth(access_key, secret_key)
        token = q.upload_token(bucket_name)
        ret, info = put_data(token, None, data)
        print(ret, info)
    except Exception as e:
        raise e;

    if info.status_code != 200:
        raise Exception("上传图片失败")
    return ret["key"]


if __name__ == '__main__':
    file = input('请输入文件路径')
    with open(file, 'rb') as f:
        storage(f.read())