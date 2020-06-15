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

    response = client.create_bucket(
        Bucket=bucket,
        ACL='public-read'  # private/public-read/public-read-write
    )
