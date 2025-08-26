import logging
from typing import Any, Dict, Optional

from pydantic import root_validator

from imarkdown.adapter.base import BaseMdAdapter
from imarkdown.config import IMarkdownConfig
from imarkdown.utils import polish_path

logger = logging.getLogger(__name__)
cfg: IMarkdownConfig = IMarkdownConfig()


class CosAdapter(BaseMdAdapter):
    name: str = "COS"
    enable_https: bool = True
    """You can use https image url if you set true, otherwise http."""
    url_prefix: str = "https"
    """Used in request url prefix"""
    secret_id: str
    """Necessary parameter when initialization."""
    secret_key: str
    """Necessary parameter when initialization."""
    bucket: str
    """Necessary parameter when initialization."""
    region: str
    """Necessary parameter when initialization."""
    custom_domain: Optional[str] = None
    """Custom domain for accessing objects"""
    client: Any

    @root_validator(pre=True)
    def validate_environment(cls, values: Optional[Dict]) -> Dict:
        # update adapter config to cache
        env_config: Dict[str, Any] = cfg.load_variable(cls.__name__)
        if env_config:
            if not values:
                values = {}
            for env_key in env_config.keys():
                if env_key not in values:
                    values.update({env_key: env_config[env_key]})
        cfg.store_variable(cls.__name__, values)

        if not values:
            raise ValueError("Please initialize your CosAdapter with parameters.")
        logger.debug(f"[imarkdown cos adapter] params: {values}")

        try:
            from qcloud_cos import CosConfig, CosS3Client

            config = CosConfig(
                Region=values["region"],
                SecretId=values["secret_id"],
                SecretKey=values["secret_key"],
                Scheme=values.get("url_prefix", "https"),
            )
            values["client"] = CosS3Client(config)

        except ImportError:
            raise ValueError(
                "Could not import qcloud_cos python package. "
                "Please install it with `pip install cos-python-sdk-v5`."
            )
        return values

    def set_enable_https(self, v: bool, values: Dict[str, Any]) -> bool:
        if v:
            self.url_prefix = "https"
        else:
            self.url_prefix = "http"

        # Update client with new scheme
        try:
            from qcloud_cos import CosConfig, CosS3Client

            config = CosConfig(
                Region=values["region"],
                SecretId=values["secret_id"],
                SecretKey=values["secret_key"],
                Scheme=self.url_prefix,
            )
            values["client"] = CosS3Client(config)
        except ImportError:
            pass

        return v

    def _join_key(self, key: str) -> str:
        """Join storage path prefix with key"""
        key = key.lstrip("/")
        if self.storage_path_prefix:
            return f"{self.storage_path_prefix.strip('/')}/{key}"
        return key

    def upload(self, key: str, file):
        """Upload file to Tencent Cloud COS"""
        final_key = self._join_key(key)

        try:
            response = self.client.put_object(
                Bucket=self.bucket, Key=final_key, Body=file
            )
            logger.info(f"[imarkdown cos adapter] uploaded {final_key} successfully")
        except Exception as e:
            logger.error(f"[imarkdown cos adapter] upload failed: {e}")
            raise

    def get_replaced_url(self, key):
        """Get the final URL for the uploaded object"""
        final_key = self._join_key(key)

        if self.custom_domain:
            # Use custom domain if provided
            return f"{self.custom_domain.rstrip('/')}/{final_key}"

        # Use standard COS domain
        return f"{self.url_prefix}://{self.bucket}.cos.{self.region}.myqcloud.com/{final_key}"
