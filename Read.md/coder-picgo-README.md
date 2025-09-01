## 开发者文档 · 新增图床（对齐 PicGo 支持）

本项目在上游 `imarkdown` 的基础上提供 GUI，一键将 Markdown 图片统一为 WebP，并按图床规则回写外链。
当前已接入阿里云 OSS，其它图床按相同流程引入：仅新增“适配器”，不改核心流程。

---

### 一、整体流程（端到端）
1. 解析 Markdown，提取图片链接（支持 `![alt](url)` 与 `<img src="...">`）。
2. 下载或读取本地图片，转换为 WebP，输出到 `images/` 目录（可自定义）。
3. 若启用图床上传：读取配置，实例化图床适配器 → 调用 `upload(key, bytes)` 上传。
4. 通过 `get_replaced_url(key)` 获取最终可访问 URL，回写到新的 Markdown 中。

说明：第 3/4 步完全遵循上游 `imarkdown` 的适配器接口，核心转换链路无需修改。

---

### 二、上游 imarkdown 核心与用法速览

- 适配器抽象（必须实现两个方法）：
```python
from imarkdown.adapter.base import BaseMdAdapter

class MyAdapter(BaseMdAdapter):
    name: str = "MyAdapter"

    def upload(self, key: str, file: bytes):
        # 将 file 上传至图床，key 为文件名（可结合 storage_path_prefix 组织路径）
        ...

    def get_replaced_url(self, key: str) -> str:
        # 返回用于回写到 Markdown 的外链 URL
        ...
```

- 转换器如何调用适配器（节选逻辑）：
```python
# 伪代码说明
if adapter.name == "Local":
    return local_relative_path
else:
    adapter.upload(image_name, file_bytes)
    return adapter.get_replaced_url(image_name)
```

- 最小使用示例（将 markdown 中图片转为图床外链）：
```python
from imarkdown import MdImageConverter, MdFile
from imarkdown.adapter.aliyun_adapter import AliyunAdapter

adapter = AliyunAdapter(
    access_key_id="...",
    access_key_secret="...",
    bucket_name="your-bucket",
    place="cn-beijing",
    storage_path_prefix="images",
)
converter = MdImageConverter(adapter=adapter)
md_file = MdFile(name="test.md")
converter.convert(md_file)
```

---

### 三、只“新增图床”该怎么做（与阿里 OSS 同流程）

目标：新增一个 `BaseMdAdapter` 子类，按 PicGo 启发的配置字段和 URL 规范实现上传与回写，不改其余代码。

步骤：
1. 在 `imarkdown/adapter/` 下新建文件：`<provider>_adapter.py`
2. 继承 `BaseMdAdapter`，实现：
   - `upload(key: str, file: bytes)`：完成鉴权、生成对象键、上传；缓存必要响应
   - `get_replaced_url(key: str) -> str`：按“自定义域名优先，其次标准域名/endpoint”生成最终 URL
3. 懒加载第三方 SDK：`try: import xxx; except ImportError: 提示 pip install xxx`
4. 若需要作为“默认适配器类型”被记忆与选择：
   - 在 `imarkdown/constant.py` 增加 `MdAdapterType.<Provider>`
   - 在 `imarkdown/adapter/__init__.py` 的 `MdAdapterMapper` 注册映射
5. 在 `example/` 加入最小示例，便于验证

注意：`storage_path_prefix` 语义与阿里云一致，用于组织远端路径前缀；最终 URL 在适配器内部规范化，核心不做分支。

---

### 四、常见图床适配器设计要点（对齐 PicGo 常用）

- 腾讯云 COS（推荐先做，和 OSS 最接近）
  - 配置：`secret_id/secret_key/bucket/region/storage_path_prefix/custom_domain?`
  - 依赖：`cos-python-sdk-v5`
  - 上传：`client.put_object(Bucket, Key, Body=file)`
  - URL：`custom_domain or https://{bucket}.cos.{region}.myqcloud.com/{prefix}/{key}`

- 七牛云 Kodo
  - 配置：`access_key/secret_key/bucket/domain/storage_path_prefix`
  - 依赖：`qiniu`
  - 上传：`put_data(upload_token, key, file)`
  - URL：`https://{domain}/{prefix}/{key}`

- S3 兼容（AWS/MinIO/Backblaze…）
  - 配置：`access_key/secret_key/bucket/region or endpoint/storage_path_prefix/custom_domain?/use_https`
  - 依赖：`boto3`
  - 上传：`client.put_object(Bucket, Key, Body=file)`
  - URL：`custom_domain 优先；否则区域域名或自定义 endpoint（支持虚拟主机式/路径式）`

- Imgur / SM.MS / Cloudinary（公共图床）
  - Imgur：`client_id` 或 Token；POST `https://api.imgur.com/3/image` → 返回 `link`
  - SM.MS：Token；POST `https://sm.ms/api/v2/upload` → `data.url`
  - Cloudinary：`cloud_name/api_key/api_secret/folder`；返回 `secure_url`

- GitHub/Gitee 仓库
  - 配置：`token/owner/repo/branch/path_prefix/custom_domain?`
  - API：PUT contents（Base64 文件内容）→ 组合 `raw/jsDelivr/custom_domain` URL

- WebDAV / SFTP（可选）
  - WebDAV：`webdavclient3` 上传到 `{base_url}/{remote_path}`，URL 可用 `custom_domain` 覆盖
  - SFTP：`paramiko` 上传，URL 需结合站点规则或自定义域名

---

### 五、示例：实现一个 COS 适配器（骨架）
```python
from typing import Optional
from pydantic import root_validator
from imarkdown.adapter.base import BaseMdAdapter

class CosAdapter(BaseMdAdapter):
    name: str = "COS"
    secret_id: str
    secret_key: str
    bucket: str
    region: str
    custom_domain: Optional[str] = None
    client: any = None

    @root_validator(pre=True)
    def _init_client(cls, values):
        try:
            from qcloud_cos import CosConfig, CosS3Client  # cos-python-sdk-v5
        except ImportError:
            raise ValueError("缺少依赖：pip install cos-python-sdk-v5")
        cfg = CosConfig(Region=values["region"], SecretId=values["secret_id"], SecretKey=values["secret_key"]) 
        values["client"] = CosS3Client(cfg)
        return values

    def _join_key(self, key: str) -> str:
        key = key.lstrip("/")
        return f"{self.storage_path_prefix}/{key}" if self.storage_path_prefix else key

    def upload(self, key: str, file: bytes):
        final_key = self._join_key(key)
        self.client.put_object(Bucket=self.bucket, Key=final_key, Body=file)

    def get_replaced_url(self, key: str) -> str:
        final_key = self._join_key(key)
        if self.custom_domain:
            return f"{self.custom_domain.rstrip('/')}/{final_key}"
        return f"https://{self.bucket}.cos.{self.region}.myqcloud.com/{final_key}"
```

---

### 六、开发与验证

- 运行 GUI（开发环境）：
```bash
pip install -r requirements.txt
python md-converter-gui/main.py
```

- 最小验证（脚本）：
```python
from imarkdown import MdImageConverter, MdFile
from imarkdown.adapter.cos_adapter import CosAdapter

adapter = CosAdapter(secret_id="...", secret_key="...", bucket="...", region="ap-beijing", storage_path_prefix="images")
converter = MdImageConverter(adapter=adapter)
converter.convert(MdFile(name="test.md"))
```

- 单测建议：
  - URL 构造与 `storage_path_prefix` 行为（纯函数/无网络）
  - 依赖缺失提示（捕获 ImportError）
  - 上传调用使用 Mock，避免真实外网请求

---

### 七、开发需求与贡献指南（简）

- 代码风格：保持清晰直观的实现与错误提示；避免在核心层增加与图床相关的分支。
- 依赖策略：适配器内部懒加载依赖，README 中补充 `pip install` 提示；尽量不增加公共必装依赖。
- 文档：为每个新图床补充最小示例与字段说明，便于快速复用。

读完本文件，你只需按“新增图床步骤”实现一个适配器，即可在不修改流程的前提下，让 GUI 与脚本两侧复用同一套 `imarkdown` 能力完成上传与外链回写。


