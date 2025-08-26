from imarkdown import MdFile, MdImageConverter
from imarkdown.adapter.github_adapter import GitHubAdapter


def main():
    """GitHub仓库适配器使用示例"""
    github_config = {
        "token": "your_github_token",  # GitHub个人访问令牌
        "owner": "your-username",  # GitHub用户名或组织名
        "repo": "your-repo-name",  # 仓库名
        "branch": "main",  # 分支名，默认为main
        "path_prefix": "images",  # 仓库中的路径前缀
        "storage_path_prefix": "md-images",  # 可选：额外的存储路径前缀
        "use_jsdelivr": False,  # 是否使用jsDelivr CDN
        "custom_domain": None,  # 可选：自定义域名
    }

    # 使用jsDelivr CDN的配置示例
    github_jsdelivr_config = {
        "token": "ghp_your_personal_access_token",
        "owner": "your-username",
        "repo": "your-repo-name",
        "branch": "main",
        "path_prefix": "assets/images",
        "use_jsdelivr": True,  # 启用jsDelivr CDN加速
    }

    # 选择一个配置
    config = github_config  # 或者 github_jsdelivr_config

    # 创建适配器
    adapter = GitHubAdapter(**config)

    # 创建转换器
    md_converter = MdImageConverter(adapter=adapter)

    # 处理Markdown文件
    md_file = MdFile(name="test.md")
    md_converter.convert(md_file)

    print("转换完成！图片已上传到GitHub仓库")


if __name__ == "__main__":
    main()
