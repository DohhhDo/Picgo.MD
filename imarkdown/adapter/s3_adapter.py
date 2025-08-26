import logging
from typing import Any, Dict, Optional

from pydantic import root_validator

from imarkdown.adapter.base import BaseMdAdapter
from imarkdown.config import IMarkdownConfig
from imarkdown.utils import polish_path

logger = logging.getLogger(__name__)
cfg: IMarkdownConfig = IMarkdownConfig()


class S3Adapter(BaseMdAdapter):
    name: str = "S3"
    access_key: str
    """AWS Access Key ID or compatible service access key."""
    secret_key: str
    """AWS Secret Access Key or compatible service secret key."""
    bucket: str
    """S3 bucket name."""
    region: Optional[str] = None
    """AWS region (e.g., us-east-1). Not required for non-AWS S3-compatible services."""
    endpoint: Optional[str] = None
    """Custom endpoint URL for S3-compatible services (e.g., MinIO, DigitalOcean Spaces)."""
    custom_domain: Optional[str] = None
    """Custom domain for accessing objects."""
    use_https: bool = True
    """Use HTTPS protocol for object URLs."""
    path_style: bool = False
    """Use path-style URLs instead of virtual-hosted-style URLs."""
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
            raise ValueError("Please initialize your S3Adapter with parameters.")
        logger.debug(f"[imarkdown s3 adapter] params: {values}")

        try:
            import boto3
            from botocore.config import Config
            
            # Prepare boto3 client configuration
            session = boto3.Session(
                aws_access_key_id=values["access_key"],
                aws_secret_access_key=values["secret_key"],
                region_name=values.get("region")
            )
            
            client_kwargs = {}
            
            # Add endpoint URL if provided (for S3-compatible services)
            if values.get("endpoint"):
                client_kwargs["endpoint_url"] = values["endpoint"]
            
            # Configure path style if requested
            if values.get("path_style", False):
                client_kwargs["config"] = Config(s3={"addressing_style": "path"})
            
            values["client"] = session.client("s3", **client_kwargs)
            
        except ImportError:
            raise ValueError(
                "Could not import boto3 python package. "
                "Please install it with `pip install boto3`."
            )
        return values

    def _join_key(self, key: str) -> str:
        """Join storage path prefix with key"""
        key = key.lstrip("/")
        if self.storage_path_prefix:
            return f"{self.storage_path_prefix.strip('/')}/{key}"
        return key

    def upload(self, key: str, file):
        """Upload file to S3 or S3-compatible service"""
        final_key = self._join_key(key)
        
        try:
            response = self.client.put_object(
                Bucket=self.bucket,
                Key=final_key,
                Body=file
            )
            logger.info(f"[imarkdown s3 adapter] uploaded {final_key} successfully")
            
        except Exception as e:
            logger.error(f"[imarkdown s3 adapter] upload failed: {e}")
            raise

    def get_replaced_url(self, key):
        """Get the final URL for the uploaded object"""
        final_key = self._join_key(key)
        
        if self.custom_domain:
            # Use custom domain if provided
            protocol = "https" if self.use_https else "http"
            return f"{protocol}://{self.custom_domain.strip('/')}/{final_key}"
        
        # Construct standard S3 URL
        protocol = "https" if self.use_https else "http"
        
        if self.endpoint:
            # For S3-compatible services with custom endpoints
            endpoint_host = self.endpoint.replace("https://", "").replace("http://", "")
            if self.path_style:
                return f"{protocol}://{endpoint_host}/{self.bucket}/{final_key}"
            else:
                return f"{protocol}://{self.bucket}.{endpoint_host}/{final_key}"
        
        # Standard AWS S3 URL
        if self.region and self.region != "us-east-1":
            if self.path_style:
                return f"{protocol}://s3.{self.region}.amazonaws.com/{self.bucket}/{final_key}"
            else:
                return f"{protocol}://{self.bucket}.s3.{self.region}.amazonaws.com/{final_key}"
        else:
            # us-east-1 region (default)
            if self.path_style:
                return f"{protocol}://s3.amazonaws.com/{self.bucket}/{final_key}"
            else:
                return f"{protocol}://{self.bucket}.s3.amazonaws.com/{final_key}"

