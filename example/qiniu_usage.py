from imarkdown import MdFile, MdImageConverter
from imarkdown.adapter.qiniu_adapter import QiniuAdapter


def main():
    """七牛云Kodo适配器使用示例"""
    qiniu_config = {
        "access_key": "your_access_key",
        "secret_key": "your_secret_key",
        "bucket": "your-bucket-name",
        "domain": "your-domain.com",  # 七牛云分配的测试域名或绑定的自定义域名
        "storage_path_prefix": "images",  # 可选：存储路径前缀
        "use_https": True,  # 是否使用HTTPS
    }

    # 创建适配器
    adapter = QiniuAdapter(**qiniu_config)

    # 创建转换器
    md_converter = MdImageConverter(adapter=adapter)

    # 处理Markdown文件
    md_file = MdFile(name="test.md")
    md_converter.convert(md_file)

    print("转换完成！图片已上传到七牛云Kodo")


if __name__ == "__main__":
    main()
