from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client

secret_id = ''  # 替换为用户的 secretId
secret_key = ''  # 替换为用户的 secretKey
region = 'ap-nanjing'  # 替换为用户的 Region

config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)

client = CosS3Client(config)

# 删除文件

# client.delete_object(
#         Bucket='km-1302167637',
#         Key='p1.jpg',  # 上传到桶之后的文件名
#     )

objects = {
    "Quiet": "true",
    "Object": [
        {
            "Key": "82aa40e5c6f9a7c47304c617aa56ef14.jpg"
        },
        {
            "Key": "c37df5ac1e74b11a24d718b6b57229af.jpg"
        },{
            "Key": "e540d78c86fa10470e5d6746347dd1f6.jpg"
        }
    ]
}
response = client.delete_objects(
                Bucket='13098935118-1592502004-1302167637',
                Delete=objects
            )
