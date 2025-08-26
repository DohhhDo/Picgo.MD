import base64
import logging
from typing import Any, Dict, Optional

from pydantic import root_validator

from imarkdown.adapter.base import BaseMdAdapter
from imarkdown.config import IMarkdownConfig
from imarkdown.utils import polish_path

logger = logging.getLogger(__name__)
cfg: IMarkdownConfig = IMarkdownConfig()


class GitHubAdapter(BaseMdAdapter):
    name: str = "GitHub"
    token: str
    """GitHub personal access token with repo permissions."""
    owner: str
    """GitHub repository owner (username or organization)."""
    repo: str
    """GitHub repository name."""
    branch: str = "main"
    """Branch to upload files to."""
    path_prefix: str = ""
    """Path prefix in the repository (e.g., 'images' or 'assets/images')."""
    custom_domain: Optional[str] = None
    """Custom domain for accessing files (e.g., CDN domain)."""
    use_jsdelivr: bool = False
    """Use jsDelivr CDN for accessing files."""

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
            raise ValueError("Please initialize your GitHubAdapter with parameters.")
        logger.debug(f"[imarkdown github adapter] params: {values}")

        # Validate required fields
        required_fields = ["token", "owner", "repo"]
        for field in required_fields:
            if not values.get(field):
                raise ValueError(f"Missing required field: {field}")

        return values

    def _join_key(self, key: str) -> str:
        """Join storage path prefix and path_prefix with key"""
        key = key.lstrip("/")
        
        # Combine both storage_path_prefix and path_prefix
        prefixes = []
        if self.storage_path_prefix:
            prefixes.append(self.storage_path_prefix.strip("/"))
        if self.path_prefix:
            prefixes.append(self.path_prefix.strip("/"))
            
        if prefixes:
            return "/".join(prefixes) + "/" + key
        return key

    def upload(self, key: str, file):
        """Upload file to GitHub repository"""
        final_key = self._join_key(key)
        
        try:
            import requests
            
            # Encode file content as base64
            if isinstance(file, bytes):
                content_b64 = base64.b64encode(file).decode('utf-8')
            else:
                # If file is a file-like object, read it
                if hasattr(file, 'read'):
                    file_content = file.read()
                else:
                    file_content = file
                if isinstance(file_content, str):
                    file_content = file_content.encode('utf-8')
                content_b64 = base64.b64encode(file_content).decode('utf-8')
            
            # GitHub API URL for creating/updating files
            api_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/contents/{final_key}"
            
            headers = {
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github.v3+json",
                "Content-Type": "application/json"
            }
            
            # Check if file exists to get SHA for update
            response = requests.get(api_url, headers=headers)
            sha = None
            if response.status_code == 200:
                sha = response.json().get("sha")
            
            # Prepare request data
            data = {
                "message": f"Upload image: {key}",
                "content": content_b64,
                "branch": self.branch
            }
            
            if sha:
                data["sha"] = sha
            
            # Upload file
            response = requests.put(api_url, headers=headers, json=data)
            
            if response.status_code not in [200, 201]:
                raise Exception(f"GitHub API error {response.status_code}: {response.text}")
                
            logger.info(f"[imarkdown github adapter] uploaded {final_key} successfully")
            
        except Exception as e:
            logger.error(f"[imarkdown github adapter] upload failed: {e}")
            raise

    def get_replaced_url(self, key):
        """Get the final URL for the uploaded file"""
        final_key = self._join_key(key)
        
        if self.custom_domain:
            # Use custom domain if provided
            return f"https://{self.custom_domain.strip('/')}/{final_key}"
        
        if self.use_jsdelivr:
            # Use jsDelivr CDN
            return f"https://cdn.jsdelivr.net/gh/{self.owner}/{self.repo}@{self.branch}/{final_key}"
        
        # Use GitHub raw content URL
        return f"https://raw.githubusercontent.com/{self.owner}/{self.repo}/{self.branch}/{final_key}"

