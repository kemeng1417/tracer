from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from django.conf import settings
from qcloud_cos.cos_exception import CosServiceError

def create_bucket(bucket, region='ap-chengdu'):
    """
    创建桶
    :param bucket: 桶名称
    :param region: 桶区域
    :return:
    """
    secret_id = settings.TENCENT_SECRET_ID  # 替换为用户的 secretId
    secret_key = settings.TENCENT_SECRET_KEY  # 替换为用户的 secretKey
    region = region  # 替换为用户的 Region

    config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)

    client = CosS3Client(config)

    client.create_bucket(
        Bucket=bucket,
        ACL='public-read'  # private/public-read/public-read-write
    )
    # 解决跨域问题
    cors_config = {
        'CORSRule': [
            {
                'AllowedOrigin': '*',
                'AllowedMethod': ['GET', 'PUT', 'HEAD', 'POST', 'DELETE'],
                'AllowedHeader': "*",
                'ExposeHeader': "*",
                'MaxAgeSeconds': 500
            }
        ]
    }
    client.put_bucket_cors(
        Bucket=bucket,
        CORSConfiguration=cors_config
    )


def upload_file(bucket, region, file_object, key):
    """
    上传文件
    :param bucket:
    :param region:
    :return:
    """
    secret_id = settings.TENCENT_SECRET_ID  # 替换为用户的 secretId
    secret_key = settings.TENCENT_SECRET_KEY  # 替换为用户的 secretKey
    region = region  # 替换为用户的 Region

    config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)

    client = CosS3Client(config)

    # 上传文件

    response = client.upload_file_from_buffer(
        Bucket=bucket,
        Body=file_object,  # 本地文件的路径
        Key=key,  # 上传到桶之后的文件名
    )
    # 返回图片路径
    return "https://{}.cos.{}.myqcloud.com/{}".format(bucket, region, key)


def delete_file(bucket, region, key):
    """
    删除单个文件
    :param bucket:
    :param region:
    :return:
    """
    secret_id = settings.TENCENT_SECRET_ID  # 替换为用户的 secretId
    secret_key = settings.TENCENT_SECRET_KEY  # 替换为用户的 secretKey
    region = region  # 替换为用户的 Region

    config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)

    client = CosS3Client(config)

    # 上传文件

    client.delete_object(
        Bucket=bucket,
        Key=key,  # 上传到桶之后的文件名
    )


def check_file(bucket, region, key):
    """校验文件是否合法"""
    secret_id = settings.TENCENT_SECRET_ID  # 替换为用户的 secretId
    secret_key = settings.TENCENT_SECRET_KEY  # 替换为用户的 secretKey
    region = region  # 替换为用户的 Region

    config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)

    client = CosS3Client(config)

    # 上传文件

    data = client.head_object(
        Bucket=bucket,
        Key=key,  # 上传到桶之后的文件名
    )
    return data


def delete_file_list(bucket, region, key_list):
    """
    批量删除文件
    :param bucket:
    :param region:
    :return:
    """
    secret_id = settings.TENCENT_SECRET_ID  # 替换为用户的 secretId
    secret_key = settings.TENCENT_SECRET_KEY  # 替换为用户的 secretKey
    region = region  # 替换为用户的 Region

    config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)

    client = CosS3Client(config)

    # 批量删除文件
    objects = {
        "Quiet": "true",
        "Object": key_list,
    }

    client.delete_objects(
        Bucket=bucket,
        Delete=objects)  # 上传到桶之后的文件名)


def credential(bucket, region, ):

    from sts.sts import Sts

    config = {
        # 临时密钥有效时长，单位是秒
        'duration_seconds': 60,
        'secret_id': settings.TENCENT_SECRET_ID,
        # 固定密钥
        'secret_key': settings.TENCENT_SECRET_KEY,
        # 设置网络代理
        # 'proxy': {
        #     'http': 'xx',
        #     'https': 'xx'
        # },
        # 换成你的 bucket
        'bucket': bucket,
        # 换成 bucket 所在地区
        'region': region,
        # 这里改成允许的路径前缀，可以根据自己网站的用户登录态判断允许上传的具体路径
        # 例子： a.jpg 或者 a/* 或者 * (使用通配符*存在重大安全风险, 请谨慎评估使用)
        'allow_prefix': '*',
        # 密钥的权限列表。简单上传和分片需要以下的权限，其他权限列表请看 https://cloud.tencent.com/document/product/436/31923
        'allow_actions': [
            # 简单上传
            # 'name/cos:PutObject',
            # 'name/cos:PostObject',
            # 分片上传
            # 'name/cos:InitiateMultipartUpload',
            # 'name/cos:ListMultipartUploads',
            # 'name/cos:ListParts',
            # 'name/cos:UploadPart',
            # 'name/cos:CompleteMultipartUpload',
            '*',
        ],

    }

    sts = Sts(config)
    # 字典中包含了临时凭证

    result_dict = sts.get_credential()

    return result_dict


def delete_bucket(bucket, region):
    """ 删除桶 """
    # - 删除桶中的所有文件
    # - 删除桶中的所有碎片
    # - 删除桶
    secret_id = settings.TENCENT_SECRET_ID  # 替换为用户的 secretId
    secret_key = settings.TENCENT_SECRET_KEY  # 替换为用户的 secretKey
    region = region  # 替换为用户的 Region

    config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
    client = CosS3Client(config)
    try:
        # 查看桶中的所有文件并删除
        while True:
            part_objects = client.list_objects(bucket)
            # 如有Contents没有值，说明已删除完毕
            contents = part_objects.get('Contents')
            if not contents:
                break
            # 批量删除
            objects = {
                'Quiet': 'true',
                'Object': [{'Key': item['Key']} for item in contents],
            }
            client.delete_objects(bucket, objects)

            # 判断是否是截断
            if part_objects['IsTruncated'] == 'false':
                break

        # 找到碎片并删除
        while True:
            part_uploads = client.list_multipart_uploads(bucket)
            uploads = part_uploads.get('Upload')
            if not uploads:
                break
            for item in uploads:
                client.abort_multipart_upload(bucket, item['Key'], item['UploadId'])

            if part_uploads['IsTruncated'] == 'false':
                break

        client.delete_bucket(bucket)
    except CosServiceError as e:
        pass
