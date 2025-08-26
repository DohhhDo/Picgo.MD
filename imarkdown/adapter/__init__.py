from typing import Dict

from imarkdown.adapter.aliyun_adapter import AliyunAdapter
from imarkdown.adapter.base import BaseMdAdapter
from imarkdown.adapter.local_adapter import LocalFileAdapter
from imarkdown.adapter.cos_adapter import CosAdapter
from imarkdown.adapter.qiniu_adapter import QiniuAdapter
from imarkdown.adapter.s3_adapter import S3Adapter
from imarkdown.adapter.github_adapter import GitHubAdapter
from imarkdown.constant import MdAdapterType

__all__ = [
    "BaseMdAdapter", "AliyunAdapter", "LocalFileAdapter", "CosAdapter", 
    "QiniuAdapter", "S3Adapter", "GitHubAdapter", "MdAdapterMapper"
]

MdAdapterMapper: Dict[str, type(BaseMdAdapter)] = {
    MdAdapterType.Local: LocalFileAdapter,
    MdAdapterType.Aliyun: AliyunAdapter,
    MdAdapterType.COS: CosAdapter,
    MdAdapterType.Qiniu: QiniuAdapter,
    MdAdapterType.S3: S3Adapter,
    MdAdapterType.GitHub: GitHubAdapter,
}
