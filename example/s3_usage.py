from imarkdown import MdFile, MdImageConverter
from imarkdown.adapter.s3_adapter import S3Adapter


def main():
    """S3兼容适配器使用示例"""

    # AWS S3 配置示例
    aws_s3_config = {
        "access_key": "your_aws_access_key",
        "secret_key": "your_aws_secret_key",
        "bucket": "your-bucket-name",
        "region": "us-east-1",  # AWS区域
        "storage_path_prefix": "images",  # 可选：存储路径前缀
        "use_https": True,
        "path_style": False,  # 使用虚拟主机风格URL
    }

    # MinIO 配置示例
    minio_config = {
        "access_key": "minioadmin",
        "secret_key": "minioadmin",
        "bucket": "images",
        "endpoint": "http://localhost:9000",  # MinIO服务地址
        "storage_path_prefix": "md-images",
        "use_https": False,
        "path_style": True,  # MinIO通常使用路径风格URL
    }

    # DigitalOcean Spaces 配置示例
    do_spaces_config = {
        "access_key": "your_do_access_key",
        "secret_key": "your_do_secret_key",
        "bucket": "your-space-name",
        "region": "nyc3",
        "endpoint": "https://nyc3.digitaloceanspaces.com",
        "storage_path_prefix": "images",
        "custom_domain": "your-cdn-domain.com",  # 可选：CDN域名
    }

    # 选择一个配置
    config = aws_s3_config  # 或者 minio_config、do_spaces_config

    # 创建适配器
    adapter = S3Adapter(**config)

    # 创建转换器
    md_converter = MdImageConverter(adapter=adapter)

    # 处理Markdown文件
    md_file = MdFile(name="test.md")
    md_converter.convert(md_file)

    print("转换完成！图片已上传到S3兼容存储")


if __name__ == "__main__":
    main()
