#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新图床适配器的测试用例
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import os
import sys

# 将imarkdown模块路径添加到sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestCosAdapter(unittest.TestCase):
    """腾讯云COS适配器测试"""
    
    def setUp(self):
        # Mock COS SDK
        self.mock_cos_config = Mock()
        self.mock_cos_client = Mock()
        
    @patch('imarkdown.adapter.cos_adapter.CosConfig')
    @patch('imarkdown.adapter.cos_adapter.CosS3Client')
    def test_cos_adapter_init(self, mock_client_class, mock_config_class):
        """测试COS适配器初始化"""
        from imarkdown.adapter.cos_adapter import CosAdapter
        
        mock_config_class.return_value = self.mock_cos_config
        mock_client_class.return_value = self.mock_cos_client
        
        adapter = CosAdapter(
            secret_id="test_id",
            secret_key="test_key", 
            bucket="test-bucket",
            region="ap-beijing",
            storage_path_prefix="images"
        )
        
        self.assertEqual(adapter.secret_id, "test_id")
        self.assertEqual(adapter.bucket, "test-bucket")
        self.assertEqual(adapter.region, "ap-beijing")
        mock_config_class.assert_called_once()
        mock_client_class.assert_called_once()
        
    @patch('imarkdown.adapter.cos_adapter.CosConfig')
    @patch('imarkdown.adapter.cos_adapter.CosS3Client')
    def test_cos_adapter_upload(self, mock_client_class, mock_config_class):
        """测试COS适配器上传功能"""
        from imarkdown.adapter.cos_adapter import CosAdapter
        
        mock_config_class.return_value = self.mock_cos_config
        mock_client_class.return_value = self.mock_cos_client
        
        adapter = CosAdapter(
            secret_id="test_id",
            secret_key="test_key",
            bucket="test-bucket", 
            region="ap-beijing",
            storage_path_prefix="images"
        )
        
        test_data = b"test file content"
        adapter.upload("test.jpg", test_data)
        
        # 验证调用了put_object方法
        self.mock_cos_client.put_object.assert_called_once_with(
            Bucket="test-bucket",
            Key="images/test.jpg",
            Body=test_data
        )
        
    @patch('imarkdown.adapter.cos_adapter.CosConfig')
    @patch('imarkdown.adapter.cos_adapter.CosS3Client')
    def test_cos_adapter_get_url(self, mock_client_class, mock_config_class):
        """测试COS适配器URL生成"""
        from imarkdown.adapter.cos_adapter import CosAdapter
        
        mock_config_class.return_value = self.mock_cos_config
        mock_client_class.return_value = self.mock_cos_client
        
        adapter = CosAdapter(
            secret_id="test_id",
            secret_key="test_key",
            bucket="test-bucket",
            region="ap-beijing",
            storage_path_prefix="images"
        )
        
        url = adapter.get_replaced_url("test.jpg")
        expected_url = "https://test-bucket.cos.ap-beijing.myqcloud.com/images/test.jpg"
        self.assertEqual(url, expected_url)


class TestQiniuAdapter(unittest.TestCase):
    """七牛云适配器测试"""
    
    @patch('imarkdown.adapter.qiniu_adapter.Auth')
    @patch('imarkdown.adapter.qiniu_adapter.put_data')
    def test_qiniu_adapter_init(self, mock_put_data, mock_auth_class):
        """测试七牛云适配器初始化"""
        from imarkdown.adapter.qiniu_adapter import QiniuAdapter
        
        mock_auth = Mock()
        mock_auth_class.return_value = mock_auth
        
        adapter = QiniuAdapter(
            access_key="test_key",
            secret_key="test_secret",
            bucket="test-bucket",
            domain="test.domain.com",
            storage_path_prefix="images"
        )
        
        self.assertEqual(adapter.access_key, "test_key")
        self.assertEqual(adapter.bucket, "test-bucket")
        self.assertEqual(adapter.domain, "test.domain.com")
        mock_auth_class.assert_called_once_with("test_key", "test_secret")
        
    @patch('imarkdown.adapter.qiniu_adapter.Auth')
    @patch('imarkdown.adapter.qiniu_adapter.put_data')
    def test_qiniu_adapter_upload(self, mock_put_data, mock_auth_class):
        """测试七牛云适配器上传功能"""
        from imarkdown.adapter.qiniu_adapter import QiniuAdapter
        
        mock_auth = Mock()
        mock_auth.upload_token.return_value = "test_token"
        mock_auth_class.return_value = mock_auth
        
        mock_info = Mock()
        mock_info.status_code = 200
        mock_put_data.return_value = ({}, mock_info)
        
        adapter = QiniuAdapter(
            access_key="test_key",
            secret_key="test_secret",
            bucket="test-bucket",
            domain="test.domain.com",
            storage_path_prefix="images"
        )
        
        test_data = b"test file content"
        adapter.upload("test.jpg", test_data)
        
        # 验证调用了相关方法
        mock_auth.upload_token.assert_called_once_with("test-bucket", "images/test.jpg")
        mock_put_data.assert_called_once_with("test_token", "images/test.jpg", test_data)


class TestS3Adapter(unittest.TestCase):
    """S3适配器测试"""
    
    @patch('imarkdown.adapter.s3_adapter.boto3')
    def test_s3_adapter_init(self, mock_boto3):
        """测试S3适配器初始化"""
        from imarkdown.adapter.s3_adapter import S3Adapter
        
        mock_session = Mock()
        mock_client = Mock()
        mock_session.client.return_value = mock_client
        mock_boto3.Session.return_value = mock_session
        
        adapter = S3Adapter(
            access_key="test_key",
            secret_key="test_secret",
            bucket="test-bucket",
            region="us-east-1",
            storage_path_prefix="images"
        )
        
        self.assertEqual(adapter.access_key, "test_key")
        self.assertEqual(adapter.bucket, "test-bucket")
        self.assertEqual(adapter.region, "us-east-1")
        mock_boto3.Session.assert_called_once()
        
    @patch('imarkdown.adapter.s3_adapter.boto3')
    def test_s3_adapter_upload(self, mock_boto3):
        """测试S3适配器上传功能"""
        from imarkdown.adapter.s3_adapter import S3Adapter
        
        mock_session = Mock()
        mock_client = Mock()
        mock_session.client.return_value = mock_client
        mock_boto3.Session.return_value = mock_session
        
        adapter = S3Adapter(
            access_key="test_key",
            secret_key="test_secret",
            bucket="test-bucket",
            region="us-east-1",
            storage_path_prefix="images"
        )
        
        test_data = b"test file content"
        adapter.upload("test.jpg", test_data)
        
        # 验证调用了put_object方法
        mock_client.put_object.assert_called_once_with(
            Bucket="test-bucket",
            Key="images/test.jpg",
            Body=test_data
        )


class TestGitHubAdapter(unittest.TestCase):
    """GitHub适配器测试"""
    
    @patch('imarkdown.adapter.github_adapter.requests')
    def test_github_adapter_init(self, mock_requests):
        """测试GitHub适配器初始化"""
        from imarkdown.adapter.github_adapter import GitHubAdapter
        
        adapter = GitHubAdapter(
            token="test_token",
            owner="test_owner",
            repo="test_repo",
            branch="main",
            storage_path_prefix="images"
        )
        
        self.assertEqual(adapter.token, "test_token")
        self.assertEqual(adapter.owner, "test_owner")
        self.assertEqual(adapter.repo, "test_repo")
        self.assertEqual(adapter.branch, "main")
        
    @patch('imarkdown.adapter.github_adapter.requests')
    @patch('imarkdown.adapter.github_adapter.base64')
    def test_github_adapter_upload(self, mock_base64, mock_requests):
        """测试GitHub适配器上传功能"""
        from imarkdown.adapter.github_adapter import GitHubAdapter
        
        # Mock base64编码
        mock_base64.b64encode.return_value.decode.return_value = "encoded_content"
        
        # Mock GitHub API响应
        mock_get_response = Mock()
        mock_get_response.status_code = 404  # 文件不存在
        
        mock_put_response = Mock()
        mock_put_response.status_code = 201
        
        mock_requests.get.return_value = mock_get_response
        mock_requests.put.return_value = mock_put_response
        
        adapter = GitHubAdapter(
            token="test_token",
            owner="test_owner",
            repo="test_repo",
            branch="main",
            storage_path_prefix="images"
        )
        
        test_data = b"test file content"
        adapter.upload("test.jpg", test_data)
        
        # 验证调用了requests.put
        mock_requests.put.assert_called_once()
        
    def test_github_adapter_get_url(self):
        """测试GitHub适配器URL生成"""
        from imarkdown.adapter.github_adapter import GitHubAdapter
        
        adapter = GitHubAdapter(
            token="test_token",
            owner="test_owner", 
            repo="test_repo",
            branch="main",
            storage_path_prefix="images"
        )
        
        url = adapter.get_replaced_url("test.jpg")
        expected_url = "https://raw.githubusercontent.com/test_owner/test_repo/main/images/test.jpg"
        self.assertEqual(url, expected_url)
        
        # 测试使用jsDelivr
        adapter.use_jsdelivr = True
        url = adapter.get_replaced_url("test.jpg")
        expected_url = "https://cdn.jsdelivr.net/gh/test_owner/test_repo@main/images/test.jpg"
        self.assertEqual(url, expected_url)


class TestAdapterIntegration(unittest.TestCase):
    """适配器集成测试"""
    
    def test_adapter_mapping(self):
        """测试适配器映射"""
        from imarkdown.adapter import MdAdapterMapper
        from imarkdown.constant import MdAdapterType
        
        # 检查所有新适配器都已注册
        self.assertIn(MdAdapterType.COS, MdAdapterMapper)
        self.assertIn(MdAdapterType.Qiniu, MdAdapterMapper)
        self.assertIn(MdAdapterType.S3, MdAdapterMapper)
        self.assertIn(MdAdapterType.GitHub, MdAdapterMapper)
        
    def test_adapter_constants(self):
        """测试适配器常量"""
        from imarkdown.constant import MdAdapterType
        
        # 检查所有新的适配器类型常量
        self.assertEqual(MdAdapterType.COS, "COS")
        self.assertEqual(MdAdapterType.Qiniu, "Qiniu")
        self.assertEqual(MdAdapterType.S3, "S3")
        self.assertEqual(MdAdapterType.GitHub, "GitHub")


if __name__ == "__main__":
    unittest.main()
