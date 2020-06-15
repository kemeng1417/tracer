from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client


secret_id = ''      # 替换为用户的 secretId
secret_key = ''      # 替换为用户的 secretKey
region = 'ap-nanjing'     # 替换为用户的 Region


config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)

client = CosS3Client(config)

# 上传文件
response = client.upload_file(
    Bucket='km-1302167637',
    LocalFilePath='test.png', # 本地文件的路径
    Key='p1.jpg', # 上传到桶之后的文件名
)
print(response['ETag'])