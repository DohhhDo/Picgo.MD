import logging
from typing import Any, Dict, Optional

from pydantic import root_validator

from imarkdown.adapter.base import BaseMdAdapter
from imarkdown.config import IMarkdownConfig
from imarkdown.utils import polish_path

logger = logging.getLogger(__name__)
cfg: IMarkdownConfig = IMarkdownConfig()


class QiniuAdapter(BaseMdAdapter):
    name: str = "Qiniu"
    access_key: str
    """Necessary parameter when initialization."""
    secret_key: str
    """Necessary parameter when initialization."""
    bucket: str
    """Necessary parameter when initialization."""
    domain: str
    """Necessary parameter when initialization. Domain for accessing objects."""
    use_https: bool = True
    """Use HTTPS protocol for object URLs"""
    auth: Any
    bucket_manager: Any

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
            raise ValueError("Please initialize your QiniuAdapter with parameters.")
        logger.debug(f"[imarkdown qiniu adapter] params: {values}")

        try:
            from qiniu import Auth, BucketManager

            values["auth"] = Auth(values["access_key"], values["secret_key"])
            values["bucket_manager"] = BucketManager(values["auth"])

        except ImportError:
            raise ValueError(
                "Could not import qiniu python package. "
                "Please install it with `pip install qiniu`."
            )
        return values

    def _join_key(self, key: str) -> str:
        """Join storage path prefix with key"""
        key = key.lstrip("/")
        if self.storage_path_prefix:
            return f"{self.storage_path_prefix.strip('/')}/{key}"
        return key

    def upload(self, key: str, file):
        """Upload file to Qiniu Kodo"""
        final_key = self._join_key(key)

        try:
            from qiniu import put_data

            # Generate upload token
            token = self.auth.upload_token(self.bucket, final_key)

            # Upload file
            ret, info = put_data(token, final_key, file)

            if info.status_code != 200:
                raise Exception(
                    f"Upload failed with status {info.status_code}: {info.text_body}"
                )

            logger.info(f"[imarkdown qiniu adapter] uploaded {final_key} successfully")

        except Exception as e:
            logger.error(f"[imarkdown qiniu adapter] upload failed: {e}")
            raise

    def get_replaced_url(self, key):
        """Get the final URL for the uploaded object"""
        final_key = self._join_key(key)

        protocol = "https" if self.use_https else "http"
        return f"{protocol}://{self.domain.strip('/')}/{final_key}"
