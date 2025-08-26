from imarkdown import MdFile, MdImageConverter
from imarkdown.adapter.cos_adapter import CosAdapter


def main():
    """腾讯云COS适配器使用示例"""
    cos_config = {
        "secret_id": "your_secret_id",
        "secret_key": "your_secret_key",
        "bucket": "your-bucket-name",
        "region": "ap-beijing",  # 例如: ap-beijing, ap-shanghai
        "storage_path_prefix": "images",  # 可选：存储路径前缀
        "custom_domain": None,  # 可选：自定义域名
    }

    # 创建适配器
    adapter = CosAdapter(**cos_config)

    # 创建转换器
    md_converter = MdImageConverter(adapter=adapter)

    # 处理Markdown文件
    md_file = MdFile(name="test.md")
    md_converter.convert(md_file)

    print("转换完成！图片已上传到腾讯云COS")


if __name__ == "__main__":
    main()
