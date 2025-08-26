#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图床扩展功能使用示例
"""

def demo_github_usage():
    """演示GitHub图床使用"""
    print("=== GitHub图床使用示例 ===")
    
    from imarkdown import MdImageConverter, MdFile
    from imarkdown.adapter.github_adapter import GitHubAdapter
    
    # 创建GitHub适配器
    github_adapter = GitHubAdapter(
        token="ghp_your_token_here",  # 你的GitHub Token
        owner="your-username",        # 你的GitHub用户名
        repo="image-storage",         # 图片存储仓库
        branch="main",                # 分支
        path_prefix="blog-images",    # 仓库中的路径前缀
        storage_path_prefix="2024",   # 存储路径前缀
        use_jsdelivr=True             # 使用jsDelivr CDN加速
    )
    
    print(f"适配器配置:")
    print(f"  仓库: {github_adapter.owner}/{github_adapter.repo}")
    print(f"  分支: {github_adapter.branch}")
    print(f"  路径: {github_adapter.path_prefix}")
    print(f"  CDN: {'jsDelivr' if github_adapter.use_jsdelivr else 'Raw'}")
    
    # 演示URL生成
    demo_url = github_adapter.get_replaced_url("example.webp")
    print(f"  生成URL: {demo_url}")
    
    print("\n使用方法:")
    print("1. 创建Markdown文件包含图片")
    print("2. 运行转换器会自动上传并替换链接")
    print("3. 转换后的Markdown使用CDN加速的图片链接")

def demo_cos_usage():
    """演示腾讯云COS使用"""
    print("\n=== 腾讯云COS使用示例 ===")
    
    # 展示配置示例（不实际创建，避免依赖问题）
    cos_config = {
        "secret_id": "AKIDxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "secret_key": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", 
        "bucket": "my-images-1234567890",
        "region": "ap-beijing",
        "storage_path_prefix": "blog",
        "custom_domain": "https://img.example.com",  # 可选
        "use_https": True
    }
    
    print("配置示例:")
    for key, value in cos_config.items():
        if 'secret' in key.lower():
            value = "*" * len(str(value))
        print(f"  {key}: {value}")
    
    print("\n生成的URL格式:")
    print("  标准: https://my-images-1234567890.cos.ap-beijing.myqcloud.com/blog/image.webp")
    print("  自定义域名: https://img.example.com/blog/image.webp")

def demo_qiniu_usage():
    """演示七牛云使用"""
    print("\n=== 七牛云Kodo使用示例 ===")
    
    qiniu_config = {
        "access_key": "your_access_key",
        "secret_key": "your_secret_key",
        "bucket": "my-storage",
        "domain": "cdn.example.com",  # 七牛分配的域名
        "storage_path_prefix": "images",
        "use_https": True
    }
    
    print("配置示例:")
    for key, value in qiniu_config.items():
        if 'secret' in key.lower() or 'key' in key.lower():
            value = "*" * 8
        print(f"  {key}: {value}")
    
    print("\n生成的URL格式:")
    print("  https://cdn.example.com/images/photo.webp")

def demo_s3_usage():
    """演示S3兼容服务使用"""
    print("\n=== S3兼容服务使用示例 ===")
    
    # AWS S3
    aws_config = {
        "access_key": "AKIAI...",
        "secret_key": "secret...",
        "bucket": "my-bucket",
        "region": "us-east-1",
        "storage_path_prefix": "uploads"
    }
    
    # MinIO
    minio_config = {
        "access_key": "minioadmin",
        "secret_key": "minioadmin",
        "bucket": "images",
        "endpoint": "http://localhost:9000",
        "path_style": True,
        "storage_path_prefix": "blog"
    }
    
    print("AWS S3配置:")
    for key, value in aws_config.items():
        if 'secret' in key.lower() or 'key' in key.lower():
            value = "*" * 8
        print(f"  {key}: {value}")
    
    print("\nMinIO配置:")
    for key, value in minio_config.items():
        if 'secret' in key.lower() or 'key' in key.lower():
            value = "*" * 8
        print(f"  {key}: {value}")

def demo_gui_usage():
    """演示GUI使用方法"""
    print("\n=== GUI使用指南 ===")
    print("1. 运行 'python md-converter-gui/main.py' 启动界面")
    print("2. 点击 '图床设置' 按钮")
    print("3. 选择图床类型：")
    print("   - 阿里云 OSS v1.6.0")
    print("   - 腾讯云 COS v5 v1.5.0")
    print("   - 七牛 v1.0")
    print("   - GitHub v1.5.0")
    print("   - S3兼容服务")
    print("4. 填写对应配置信息")
    print("5. 点击 '测试上传' 验证配置")
    print("6. 保存配置")
    print("7. 在主界面输入Markdown内容并转换")

def main():
    print("🚀 图床扩展功能使用演示\n")
    print("本项目现已支持以下图床类型:")
    print("✅ 阿里云OSS (原有)")
    print("✅ 腾讯云COS v5 (新增)")
    print("✅ 七牛云Kodo (新增)")
    print("✅ S3兼容服务 (新增) - 支持AWS S3, MinIO, DigitalOcean Spaces等")
    print("✅ GitHub仓库 (新增) - 支持jsDelivr CDN加速")
    
    demo_github_usage()
    demo_cos_usage()
    demo_qiniu_usage()
    demo_s3_usage()
    demo_gui_usage()
    
    print("\n🎯 功能特点:")
    print("- 完全对齐PicGo图床支持")
    print("- 保持原项目架构一致性")
    print("- 支持自定义域名和CDN加速")
    print("- 提供友好的GUI配置界面")
    print("- 包含详细的使用示例和文档")
    
    print("\n📚 更多信息:")
    print("- 查看 example/ 目录下的使用示例")
    print("- 参考 图床扩展完成总结.md 了解详细功能")
    print("- 运行 python test_integration.py 验证功能")

if __name__ == "__main__":
    main()
