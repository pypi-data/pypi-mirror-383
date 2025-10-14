"""API client for MCP ToolBox"""

import requests
from typing import Optional, Dict, Any, List
from pathlib import Path


class ToolBoxClient:
    """Client for interacting with MCP ToolBox API"""

    def __init__(self, api_url: str, api_token: Optional[str] = None):
        self.api_url = api_url.rstrip('/')
        self.api_token = api_token
        self.session = requests.Session()
        if api_token:
            self.session.headers['Authorization'] = f'Bearer {api_token}'

    def login(self, email: str, password: str) -> str:
        """Login and return access token"""
        response = self.session.post(
            f'{self.api_url}/api/auth/login',
            data={'username': email, 'password': password}
        )
        response.raise_for_status()
        data = response.json()
        return data['access_token']

    def get_user_info(self) -> Dict[str, Any]:
        """Get current user information"""
        response = self.session.get(f'{self.api_url}/api/auth/me')
        response.raise_for_status()
        return response.json()

    def list_tools(self, page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """List available tools"""
        response = self.session.get(
            f'{self.api_url}/api/tools',
            params={'page': page, 'page_size': page_size}
        )
        response.raise_for_status()
        return response.json()

    def upload_tool(
        self,
        name: str,
        version: str,
        description: str,
        file_path: Path,
        tags: Optional[list] = None,
        thumbnail_path: Optional[Path] = None
    ) -> Dict[str, Any]:
        """Upload a new tool"""
        import json

        files = {}

        # Prepare metadata as JSON string
        metadata = {
            'author': 'Unknown',
            'tags': tags or [],
            'category': 'general',
            'license': 'MIT',
            'repository': '',
            'tools': []
        }

        data = {
            'name': name,
            'version': version,
            'description': description,
            'metadata': json.dumps(metadata),
            'tags': json.dumps(tags or [])
        }

        # Add the main file
        files['file'] = (file_path.name, open(file_path, 'rb'))

        # Add thumbnail if provided
        if thumbnail_path and thumbnail_path.exists():
            files['thumbnail'] = (thumbnail_path.name, open(thumbnail_path, 'rb'))

        try:
            response = self.session.post(
                f'{self.api_url}/api/tools/upload',
                data=data,
                files=files
            )
            response.raise_for_status()
            return response.json()
        finally:
            # Close file handles
            for f in files.values():
                if hasattr(f[1], 'close'):
                    f[1].close()

    def create_version(
        self,
        tool_id: str,
        version: str,
        file_path: Path,
        changelog: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new version of an existing tool"""
        files = {'file': (file_path.name, open(file_path, 'rb'))}
        data = {'version': version}

        if changelog:
            data['changelog'] = changelog

        try:
            response = self.session.post(
                f'{self.api_url}/api/tools/{tool_id}/versions',
                data=data,
                files=files
            )
            response.raise_for_status()
            return response.json()
        finally:
            files['file'][1].close()

    def update_thumbnail(self, tool_id: str, thumbnail_path: Path) -> Dict[str, Any]:
        """Update tool thumbnail"""
        files = {'thumbnail': (thumbnail_path.name, open(thumbnail_path, 'rb'))}

        try:
            response = self.session.put(
                f'{self.api_url}/api/tools/{tool_id}/thumbnail',
                files=files
            )
            response.raise_for_status()
            return response.json()
        finally:
            files['thumbnail'][1].close()

    def upload_from_github(
        self,
        github_url: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        version: Optional[str] = None
    ) -> Dict[str, Any]:
        """Upload a tool from GitHub repository"""
        data = {'github_url': github_url}
        
        if name:
            data['name'] = name
        if description:
            data['description'] = description
        if version:
            data['version'] = version
            
        response = self.session.post(
            f'{self.api_url}/api/tools/upload/github',
            json=data
        )
        response.raise_for_status()
        return response.json()

    def update_from_github(self, tool_id: str) -> Dict[str, Any]:
        """Update tool from its GitHub repository"""
        response = self.session.post(
            f'{self.api_url}/api/tools/{tool_id}/update-from-github'
        )
        response.raise_for_status()
        return response.json()

    def download_tool(self, tool_id: str, output_path: Optional[Path] = None) -> Path:
        """Download a tool"""
        response = self.session.get(f'{self.api_url}/api/tools/{tool_id}/download')
        response.raise_for_status()
        
        # Get filename from Content-Disposition header or use tool_id
        filename = f"{tool_id}.zip"
        if 'Content-Disposition' in response.headers:
            import re
            match = re.search(r'filename="(.+)"', response.headers['Content-Disposition'])
            if match:
                filename = match.group(1)
        
        if output_path is None:
            output_path = Path(filename)
        elif output_path.is_dir():
            output_path = output_path / filename
            
        with open(output_path, 'wb') as f:
            f.write(response.content)
            
        return output_path

    def search_tools(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """Search for tools"""
        params = {
            'q': query,
            'page': page,
            'page_size': page_size
        }
        
        if filters:
            for key, value in filters.items():
                if key == 'tags' and isinstance(value, list):
                    params['tags'] = ','.join(value)
                else:
                    params[key] = value
                    
        response = self.session.get(
            f'{self.api_url}/api/tools',
            params=params
        )
        response.raise_for_status()
        return response.json()

    def create_personal_token(self, name: str, expires_days: Optional[int] = None) -> Dict[str, Any]:
        """Create a Personal Access Token"""
        data = {'name': name}
        if expires_days:
            data['expires_days'] = expires_days
            
        response = self.session.post(
            f'{self.api_url}/api/tokens',
            json=data
        )
        response.raise_for_status()
        return response.json()

    def list_personal_tokens(self) -> List[Dict[str, Any]]:
        """List Personal Access Tokens"""
        response = self.session.get(f'{self.api_url}/api/tokens')
        response.raise_for_status()
        return response.json()

    def delete_personal_token(self, token_id: str) -> None:
        """Delete a Personal Access Token"""
        response = self.session.delete(f'{self.api_url}/api/tokens/{token_id}')
        response.raise_for_status()

    def get_tool_info(self, tool_id: str) -> Dict[str, Any]:
        """Get detailed tool information"""
        response = self.session.get(f'{self.api_url}/api/tools/{tool_id}')
        response.raise_for_status()
        return response.json()

    def get_tool_versions(self, tool_id: str) -> List[Dict[str, Any]]:
        """Get tool versions"""
        response = self.session.get(f'{self.api_url}/api/tools/{tool_id}/versions')
        response.raise_for_status()
        return response.json()

    def download_tool_version(self, tool_id: str, version_id: str, output_path: Optional[Path] = None) -> Path:
        """Download a specific tool version"""
        response = self.session.get(f'{self.api_url}/api/tools/{tool_id}/versions/{version_id}/download')
        response.raise_for_status()
        
        # Get filename from Content-Disposition header or use tool_id_version
        filename = f"{tool_id}_v{version_id}.zip"
        if 'Content-Disposition' in response.headers:
            import re
            match = re.search(r'filename="(.+)"', response.headers['Content-Disposition'])
            if match:
                filename = match.group(1)
        
        if output_path is None:
            output_path = Path(filename)
        elif output_path.is_dir():
            output_path = output_path / filename
            
        with open(output_path, 'wb') as f:
            f.write(response.content)
            
        return output_path
