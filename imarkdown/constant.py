from enum import Enum
from typing import Dict


class MdAdapterType(str, Enum):
    Local = "Local"
    Aliyun = "Aliyun"
    COS = "COS"
    Qiniu = "Qiniu"
    S3 = "S3"
    GitHub = "GitHub"


_MdAdapterType: Dict[str, str] = {
    MdAdapterType.Local: MdAdapterType.Local,
    MdAdapterType.Aliyun: MdAdapterType.Aliyun,
    MdAdapterType.COS: MdAdapterType.COS,
    MdAdapterType.Qiniu: MdAdapterType.Qiniu,
    MdAdapterType.S3: MdAdapterType.S3,
    MdAdapterType.GitHub: MdAdapterType.GitHub,
}
