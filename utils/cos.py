from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from django.conf import settings


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
