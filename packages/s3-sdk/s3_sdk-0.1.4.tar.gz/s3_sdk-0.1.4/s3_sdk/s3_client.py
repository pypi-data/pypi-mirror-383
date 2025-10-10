import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
from typing import Optional, Union
from io import BytesIO
import logging

class S3Client:
    def __init__(self, ak: Optional[str] = None, sk: Optional[str] = None, region: Optional[str] = None, endpoint_url: Optional[str] = None):
        """初始化 S3 客户端"""
        self.client = boto3.client(
            's3',
            aws_access_key_id=ak,
            aws_secret_access_key=sk,
            region_name=region,
            endpoint_url=endpoint_url,
            config=Config(signature_version='s3v4')
        )

    def put_object(self, bucket: str, key: str, content: Union[bytes, str], content_type: Optional[str] = 'application/octet-stream'):
        """上传字节内容到 S3"""
        self.client.put_object(
            Bucket=bucket,
            Key=key,
            Body=content,
            ContentType=content_type
        )
        logging.info(f"文件已上传至 {bucket}/{key}")

    def put_object_from_file(self, bucket: str, key: str, file_path: str, content_type: Optional[str] = 'application/octet-stream'):
        """从文件路径上传文件到 S3"""
        self.client.upload_file(file_path, bucket, key)
        logging.info(f"文件已上传至 {bucket}/{key}")

    def download(self, bucket: str, key: str) -> BytesIO:
        """从 S3 下载文件"""
        try:
            response = self.client.get_object(Bucket=bucket, Key=key)
            return BytesIO(response['Body'].read())
        except ClientError as e:
            logging.error(f"下载失败: {e}")
            raise
    
    def download_file(self, bucket: str, key: str, file_path: str):
        """从 S3 下载文件到本地"""
        self.client.download_file(bucket, key, file_path)
        logging.info(f"文件已下载至 {file_path}")
        return file_path

    def exists(self, bucket: str, key: str) -> bool:
        """检查对象是否存在于 S3"""
        try:
            self.client.head_object(Bucket=bucket, Key=key)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            logging.error(f"检查对象存在性失败: {e}")
            raise

    def generate_presigned_url(self, bucket: str, key: str, operation: str, expires_in: int = 3600) -> str:
        """生成 S3 临时签名 URL"""
        try:
            url = self.client.generate_presigned_url(
                ClientMethod=operation,
                Params={'Bucket': bucket, 'Key': key},
                ExpiresIn=expires_in
            )
            return url
        except ClientError as e:
            logging.error(f"生成临时签名 URL 失败: {e}")
            raise

    def list_buckets(self) -> list[str]:
        """列出所有 S3 桶名称"""
        try:
            response = self.client.list_buckets()
            buckets = [bucket['Name'] for bucket in response.get('Buckets', [])]
            return buckets
        except ClientError as e:
            logging.error(f"列出桶失败: {e}")
            raise

