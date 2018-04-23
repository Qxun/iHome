# -*- coding: utf-8 -*-
import qiniu

access_key = 'uzc59bVURbUbazey9vrexXKocNKBUN8NuLijk57N'
secret_key = '-9lenw28jU2REojvGkcsEPWk5Nm9V2HIVqb5Nkts'

# 存储空间名称
bucket_name = 'ihome26'

def image_storage(data):
    # 初始化
    q = qiniu.Auth(access_key, secret_key)

    # 指定上传文件保存的存储空间名称
    token = q.upload_token(bucket_name)

    # 上传文件
    ret, info = qiniu.put_data(token, None, data)
    if info.status_code == 200:
        #上传成功
        key = ret.get('key')
        print key
        return key
    else:
        raise Exception('上传文件到七牛云失败')

if __name__ == '__main__':

    file_name = raw_input('请输入要上传的文件')
    with open(file_name, 'rb') as f:
        image_storage(f.read())