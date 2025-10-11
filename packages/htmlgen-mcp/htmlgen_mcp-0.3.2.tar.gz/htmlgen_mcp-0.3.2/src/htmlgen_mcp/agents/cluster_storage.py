#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集群文件存储模块 - 支持对象存储
"""

import os
import mimetypes
from pathlib import Path
from typing import Optional, List


class StorageBackend:
    """存储后端抽象基类"""
    
    def upload_file(self, local_path: str, remote_path: str) -> str:
        """
        上传文件到存储
        
        Args:
            local_path: 本地文件路径
            remote_path: 远程存储路径
            
        Returns:
            可访问的 URL
        """
        raise NotImplementedError
    
    def download_file(self, remote_path: str, local_path: str) -> bool:
        """下载文件到本地"""
        raise NotImplementedError
    
    def delete_file(self, remote_path: str) -> bool:
        """删除文件"""
        raise NotImplementedError
    
    def list_files(self, prefix: str) -> List[str]:
        """列出指定前缀的所有文件"""
        raise NotImplementedError
    
    def get_url(self, remote_path: str, expires: int = 3600) -> str:
        """获取文件访问URL"""
        raise NotImplementedError


class LocalStorageBackend(StorageBackend):
    """
    本地文件系统存储（开发/单机环境）
    适用于开发测试，生产环境请使用对象存储
    """
    
    def __init__(self, base_dir: str = "/tmp/agent_storage"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def upload_file(self, local_path: str, remote_path: str) -> str:
        """复制文件到存储目录"""
        target_path = self.base_dir / remote_path
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        import shutil
        shutil.copy2(local_path, target_path)
        
        return f"file://{target_path}"
    
    def download_file(self, remote_path: str, local_path: str) -> bool:
        """从存储目录复制文件"""
        source_path = self.base_dir / remote_path
        if not source_path.exists():
            return False
        
        import shutil
        Path(local_path).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, local_path)
        return True
    
    def delete_file(self, remote_path: str) -> bool:
        """删除文件"""
        target_path = self.base_dir / remote_path
        if target_path.exists():
            target_path.unlink()
            return True
        return False
    
    def list_files(self, prefix: str) -> List[str]:
        """列出文件"""
        prefix_path = self.base_dir / prefix
        if not prefix_path.exists():
            return []
        
        files = []
        for file_path in prefix_path.rglob("*"):
            if file_path.is_file():
                rel_path = file_path.relative_to(self.base_dir)
                files.append(str(rel_path))
        return files
    
    def get_url(self, remote_path: str, expires: int = 3600) -> str:
        """获取文件URL"""
        target_path = self.base_dir / remote_path
        return f"file://{target_path}"


class OSSStorageBackend(StorageBackend):
    """阿里云 OSS 存储"""
    
    def __init__(self, access_key: str, secret_key: str, endpoint: str, bucket: str):
        try:
            import oss2
        except ImportError:
            raise ImportError("请安装 oss2: pip install oss2")
        
        auth = oss2.Auth(access_key, secret_key)
        self.bucket = oss2.Bucket(auth, endpoint, bucket)
        self.bucket_name = bucket
        self.endpoint = endpoint
    
    def upload_file(self, local_path: str, remote_path: str) -> str:
        """上传文件到 OSS"""
        # 自动检测 Content-Type
        content_type, _ = mimetypes.guess_type(local_path)
        
        headers = {}
        if content_type:
            headers['Content-Type'] = content_type
        
        self.bucket.put_object_from_file(remote_path, local_path, headers=headers)
        
        return f"https://{self.bucket_name}.{self.endpoint}/{remote_path}"
    
    def download_file(self, remote_path: str, local_path: str) -> bool:
        """从 OSS 下载文件"""
        try:
            Path(local_path).parent.mkdir(parents=True, exist_ok=True)
            self.bucket.get_object_to_file(remote_path, local_path)
            return True
        except Exception:
            return False
    
    def delete_file(self, remote_path: str) -> bool:
        """删除 OSS 文件"""
        try:
            self.bucket.delete_object(remote_path)
            return True
        except Exception:
            return False
    
    def list_files(self, prefix: str) -> List[str]:
        """列出 OSS 文件"""
        files = []
        for obj in oss2.ObjectIterator(self.bucket, prefix=prefix):
            files.append(obj.key)
        return files
    
    def get_url(self, remote_path: str, expires: int = 3600) -> str:
        """获取 OSS 签名 URL"""
        return self.bucket.sign_url('GET', remote_path, expires)


class S3StorageBackend(StorageBackend):
    """AWS S3 / MinIO 存储"""
    
    def __init__(self, access_key: str, secret_key: str, endpoint: str, bucket: str, region: str = "us-east-1"):
        try:
            import boto3
        except ImportError:
            raise ImportError("请安装 boto3: pip install boto3")
        
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            endpoint_url=endpoint if endpoint else None,
            region_name=region
        )
        self.bucket = bucket
        self.endpoint = endpoint
    
    def upload_file(self, local_path: str, remote_path: str) -> str:
        """上传文件到 S3"""
        content_type, _ = mimetypes.guess_type(local_path)
        
        extra_args = {}
        if content_type:
            extra_args['ContentType'] = content_type
        
        self.s3_client.upload_file(local_path, self.bucket, remote_path, ExtraArgs=extra_args)
        
        if self.endpoint:
            return f"{self.endpoint}/{self.bucket}/{remote_path}"
        return f"https://{self.bucket}.s3.amazonaws.com/{remote_path}"
    
    def download_file(self, remote_path: str, local_path: str) -> bool:
        """从 S3 下载文件"""
        try:
            Path(local_path).parent.mkdir(parents=True, exist_ok=True)
            self.s3_client.download_file(self.bucket, remote_path, local_path)
            return True
        except Exception:
            return False
    
    def delete_file(self, remote_path: str) -> bool:
        """删除 S3 文件"""
        try:
            self.s3_client.delete_object(Bucket=self.bucket, Key=remote_path)
            return True
        except Exception:
            return False
    
    def list_files(self, prefix: str) -> List[str]:
        """列出 S3 文件"""
        files = []
        paginator = self.s3_client.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=self.bucket, Prefix=prefix):
            if 'Contents' in page:
                for obj in page['Contents']:
                    files.append(obj['Key'])
        return files
    
    def get_url(self, remote_path: str, expires: int = 3600) -> str:
        """获取 S3 签名 URL"""
        return self.s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucket, 'Key': remote_path},
            ExpiresIn=expires
        )


class COSStorageBackend(StorageBackend):
    """腾讯云 COS 存储"""
    
    def __init__(self, secret_id: str, secret_key: str, region: str, bucket: str):
        try:
            from qcloud_cos import CosConfig, CosS3Client
        except ImportError:
            raise ImportError("请安装 cos-python-sdk-v5: pip install cos-python-sdk-v5")
        
        config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
        self.client = CosS3Client(config)
        self.bucket = bucket
        self.region = region
    
    def upload_file(self, local_path: str, remote_path: str) -> str:
        """上传文件到 COS"""
        content_type, _ = mimetypes.guess_type(local_path)
        
        with open(local_path, 'rb') as f:
            self.client.put_object(
                Bucket=self.bucket,
                Body=f,
                Key=remote_path,
                ContentType=content_type or 'application/octet-stream'
            )
        
        return f"https://{self.bucket}.cos.{self.region}.myqcloud.com/{remote_path}"
    
    def download_file(self, remote_path: str, local_path: str) -> bool:
        """从 COS 下载文件"""
        try:
            Path(local_path).parent.mkdir(parents=True, exist_ok=True)
            response = self.client.get_object(Bucket=self.bucket, Key=remote_path)
            response['Body'].get_stream_to_file(local_path)
            return True
        except Exception:
            return False
    
    def delete_file(self, remote_path: str) -> bool:
        """删除 COS 文件"""
        try:
            self.client.delete_object(Bucket=self.bucket, Key=remote_path)
            return True
        except Exception:
            return False
    
    def list_files(self, prefix: str) -> List[str]:
        """列出 COS 文件"""
        files = []
        marker = ""
        while True:
            response = self.client.list_objects(Bucket=self.bucket, Prefix=prefix, Marker=marker)
            if 'Contents' in response:
                for obj in response['Contents']:
                    files.append(obj['Key'])
            if response['IsTruncated'] == 'false':
                break
            marker = response['NextMarker']
        return files
    
    def get_url(self, remote_path: str, expires: int = 3600) -> str:
        """获取 COS 签名 URL"""
        return self.client.get_presigned_download_url(
            Bucket=self.bucket,
            Key=remote_path,
            Expired=expires
        )


def create_storage_backend(
    backend_type: str = "local",
    **kwargs
) -> StorageBackend:
    """
    工厂函数：创建存储后端
    
    Args:
        backend_type: 后端类型 'local', 'oss', 's3', 'cos'
        **kwargs: 各后端的配置参数
            - local: base_dir
            - oss: access_key, secret_key, endpoint, bucket
            - s3: access_key, secret_key, endpoint, bucket, region
            - cos: secret_id, secret_key, region, bucket
    
    Returns:
        StorageBackend 实例
    """
    if backend_type == "local":
        return LocalStorageBackend(kwargs.get("base_dir", "/tmp/agent_storage"))
    elif backend_type == "oss":
        return OSSStorageBackend(
            access_key=kwargs["access_key"],
            secret_key=kwargs["secret_key"],
            endpoint=kwargs["endpoint"],
            bucket=kwargs["bucket"]
        )
    elif backend_type == "s3":
        return S3StorageBackend(
            access_key=kwargs["access_key"],
            secret_key=kwargs["secret_key"],
            endpoint=kwargs.get("endpoint"),
            bucket=kwargs["bucket"],
            region=kwargs.get("region", "us-east-1")
        )
    elif backend_type == "cos":
        return COSStorageBackend(
            secret_id=kwargs["secret_id"],
            secret_key=kwargs["secret_key"],
            region=kwargs["region"],
            bucket=kwargs["bucket"]
        )
    else:
        raise ValueError(f"不支持的存储后端: {backend_type}")
