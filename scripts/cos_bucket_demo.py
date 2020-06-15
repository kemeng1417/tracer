from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client


secret_id = ''      # 替换为用户的 secretId
secret_key = ''      # 替换为用户的 secretKey
region = 'ap-nanjing'     # 替换为用户的 Region


config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)

client = CosS3Client(config)


response = client.create_bucket(
    Bucket='test-1302167637',
    ACL='public-read'# private/public-read/public-read-write
)