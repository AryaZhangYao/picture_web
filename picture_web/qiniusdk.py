# -*- coding: utf-8 -*-
# flake8: noqa
from picture_web1.picture_web import app
from qiniu import Auth, put_file, etag
import os
import qiniu.config
#需要填写你的 Access Key 和 Secret Key
access_key = app.config['QINIU_ACCESS_KEY']
secret_key = app.config['QINIU_SECRET_KEY']
#构建鉴权对象
q = Auth(access_key, secret_key)
#要上传的空间
bucket_name = app.config['QINIU_BUCKET_NAME']
#URL前缀
domain_prefix = app.config['QINIU_DOMAIN']
#上传后保存的文件名
# key = 'my-python-logo.png'
#生成上传 Token，可以指定过期时间等
# token = q.upload_token(bucket_name, key, 3600)
#要上传文件的本地路径
save_dir = app.config['UPLOAD_DIR']
def qiniu_upload_file(source_file, save_file_name):
    token = q.upload_token(bucket_name, save_file_name, 3600)
    source_file.save(os.path.join(save_dir,save_file_name))
    ret, info = put_file(token, save_file_name, os.path.join(save_dir,save_file_name))
    print(info)
    # assert ret['key'] == save_file_name
    # assert ret['hash'] == etag(localfile)
    if info.status_code == 200:
        return domain_prefix + save_file_name
    return None