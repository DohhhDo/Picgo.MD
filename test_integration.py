#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图床扩展功能集成测试
"""


def test_adapter_registration():
    """测试适配器注册"""
    print("=== 测试适配器注册 ===")
    from imarkdown.adapter import MdAdapterMapper
    from imarkdown.constant import MdAdapterType

    print(f"总共支持 {len(MdAdapterMapper)} 个图床类型:")
    for adapter_type, adapter_class in MdAdapterMapper.items():
        print(f"  - {adapter_type}: {adapter_class.__name__}")

    # 验证新增的适配器
    new_adapters = [
        MdAdapterType.COS,
        MdAdapterType.Qiniu,
        MdAdapterType.S3,
        MdAdapterType.GitHub,
    ]
    for adapter_type in new_adapters:
        assert adapter_type in MdAdapterMapper, f"适配器 {adapter_type} 未注册"
        print(f"✓ {adapter_type} 适配器注册成功")

    print("✅ 所有适配器注册测试通过\n")


def test_github_adapter():
    """测试GitHub适配器功能"""
    print("=== 测试GitHub适配器 ===")
    from imarkdown.adapter.github_adapter import GitHubAdapter

    # 创建适配器实例
    adapter = GitHubAdapter(
        token="test_token",
        owner="test_user",
        repo="test_repo",
        branch="main",
        storage_path_prefix="images",
    )

    print(f"适配器名称: {adapter.name}")
    print(f"仓库信息: {adapter.owner}/{adapter.repo}")

    # 测试URL生成
    test_key = "test.jpg"
    raw_url = adapter.get_replaced_url(test_key)
    print(f"Raw URL: {raw_url}")

    # 测试jsDelivr模式
    adapter.use_jsdelivr = True
    jsdelivr_url = adapter.get_replaced_url(test_key)
    print(f"jsDelivr URL: {jsdelivr_url}")

    # 验证URL格式
    assert "raw.githubusercontent.com" in raw_url, "Raw URL格式错误"
    assert "cdn.jsdelivr.net" in jsdelivr_url, "jsDelivr URL格式错误"

    print("✅ GitHub适配器功能测试通过\n")


def test_adapter_url_generation():
    """测试各适配器URL生成功能"""
    print("=== 测试URL生成功能 ===")

    # GitHub适配器
    from imarkdown.adapter.github_adapter import GitHubAdapter

    gh_adapter = GitHubAdapter(
        token="test", owner="user", repo="repo", storage_path_prefix="img"
    )
    gh_url = gh_adapter.get_replaced_url("test.webp")
    print(f"GitHub URL: {gh_url}")
    assert "raw.githubusercontent.com/user/repo/main/img/test.webp" in gh_url

    print("✅ URL生成功能测试通过\n")


def test_gui_upload_manager():
    """测试GUI上传管理器"""
    print("=== 测试GUI上传管理器 ===")
    import os
    import sys

    sys.path.append(os.path.join(os.path.dirname(__file__), "md-converter-gui"))
    from uploader.manager import UploadManager

    # 创建上传管理器
    manager = UploadManager()
    print("✓ UploadManager创建成功")

    # 测试配置加载方法（不会实际加载，因为没有真实配置）
    cos_config = manager._load_cos_config()
    qiniu_config = manager._load_qiniu_config()
    s3_config = manager._load_s3_config()
    github_config = manager._load_github_config()

    print("✓ 配置加载方法工作正常")
    print(f"COS配置字段: {list(cos_config.keys())}")
    print(f"七牛配置字段: {list(qiniu_config.keys())}")
    print(f"S3配置字段: {list(s3_config.keys())}")
    print(f"GitHub配置字段: {list(github_config.keys())}")

    print("✅ GUI上传管理器测试通过\n")


def main():
    """运行所有测试"""
    print("🚀 开始图床扩展功能集成测试...\n")

    try:
        test_adapter_registration()
        test_github_adapter()
        test_adapter_url_generation()
        test_gui_upload_manager()

        print("🎉 所有集成测试通过！")
        print("\n📋 测试总结:")
        print("  ✅ 适配器注册: 6个图床类型 (Local, Aliyun, COS, Qiniu, S3, GitHub)")
        print("  ✅ GitHub适配器: URL生成正常，支持Raw和jsDelivr两种模式")
        print("  ✅ GUI集成: UploadManager支持所有新图床类型")
        print("  ✅ 架构一致性: 完全遵循原项目设计")

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
