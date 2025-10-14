"""Main client for KITECH Repository API."""

import asyncio
import zipfile
import tempfile
from pathlib import Path
from typing import Dict, List, Optional

import httpx
from tqdm import tqdm

from kitech_repository.core.auth import AuthManager
from kitech_repository.core.config import Config
from kitech_repository.core.exceptions import ApiError, AuthenticationError, DownloadError, UploadError
from kitech_repository.models.file import File, FileDownloadInfo
from kitech_repository.models.repository import Repository


class KitechClient:
    """Main client for interacting with KITECH Repository API."""

    def __init__(self, config: Optional[Config] = None, token: Optional[str] = None):
        """Initialize KITECH client."""
        self.config = config or Config.load()
        self.auth_manager = AuthManager(self.config)

        if token:
            self.auth_manager.login(token=token)

        self.client = httpx.Client(
            base_url=self.config.api_base_url,
            timeout=httpx.Timeout(600.0, connect=30.0),  # 10 minutes total, 30s connect
            headers=self.auth_manager.headers if self.auth_manager.is_authenticated() else {},
        )
    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, *args):
        """Context manager exit."""
        self.close()

    def close(self):
        """Close the HTTP client."""
        self.client.close()

    def test_connection(self) -> Dict:
        """Test connection and authentication to the API."""
        try:
            response = self.client.get("/test")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Invalid or expired API token")
            raise ApiError(f"API request failed: {e}")
        except Exception as e:
            raise ApiError(f"Connection test failed: {e}")

    def list_repositories(
        self,
        page: int = 0,
        limit: int = 20,
        include_shared: bool = True
    ) -> Dict[str, List[Repository]]:
        """List available repositories."""
        params = {
            "page": page,
            "limit": limit,
            "includeShared": include_shared,
        }

        try:
            response = self.client.get("/repositories", params=params)
            response.raise_for_status()
            data = response.json()

            repositories = [
                Repository(**repo) for repo in data.get("repositories", [])
            ]

            return {
                "repositories": repositories,
                "total_count": data.get("totalCount", 0),
            }
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Invalid or expired API token")
            raise ApiError(f"Failed to list repositories: {e}")

    def list_files(
        self,
        repository_id: int,
        prefix: str = "",
        search: Optional[str] = None,
        include_hash: bool = False,
        limit: int = 100,
        page: int = 0
    ) -> Dict[str, List[File]]:
        """List files in a dataset (repository)."""
        params = {
            "limit": limit,
            "page": page
        }
        if prefix:
            params["prefix"] = prefix
        if search:
            params["search"] = search
        if include_hash:
            params["includeHash"] = include_hash

        try:
            response = self.client.get(
                f"/datasets/{repository_id}/files",
                params=params
            )
            response.raise_for_status()
            data = response.json()

            # Handle new API response structure with 'content' and 'meta'
            content = data.get("content", [])
            meta = data.get("meta", {})

            files = [
                File(**file_data) for file_data in content
            ]

            return {
                "files": files,
                "repository_id": repository_id,
                "prefix": prefix,  # Use the prefix we sent
                "total_count": meta.get("total", len(files)),
                "has_more": meta.get("page", 0) < meta.get("maxPage", 0) - 1 if "maxPage" in meta else False,
                "page": meta.get("page", 0),
                "limit": meta.get("limit", limit),
            }
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Invalid or expired API token")
            elif e.response.status_code == 404:
                raise ApiError(f"Repository {repository_id} not found")
            raise ApiError(f"Failed to list files: {e}")

    def get_download_url(
        self,
        repository_id: int,
        path: Optional[str] = None
    ) -> str:
        """Get download URL for a file or folder."""
        params = {}
        if path:
            params["path"] = path

        try:
            response = self.client.get(
                f"/repositories/{repository_id}/download",
                params=params
            )
            response.raise_for_status()
            data = response.json()

            # Handle new API response structure
            if data.get("success") and "downloadUrl" in data:
                return data["downloadUrl"]
            else:
                # Fallback for old response format
                return data.get("downloadUrl")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Invalid or expired API token")
            elif e.response.status_code == 404:
                raise ApiError(f"Repository or path not found")
            raise ApiError(f"Failed to get download URL: {e}")

    def download_file(
        self,
        repository_id: int,
        path: Optional[str] = None,
        output_dir: Optional[Path] = None,
        show_progress: bool = True,
        is_directory: bool = False
    ) -> Path:
        """Download a file or folder from repository."""
        download_url = self.get_download_url(repository_id, path)

        # Convert string to Path if necessary
        if output_dir is not None and not isinstance(output_dir, Path):
            output_dir = Path(output_dir)

        output_dir = output_dir or self.config.download_dir
        output_dir.mkdir(parents=True, exist_ok=True)

        # Determine if this is a ZIP download
        # - path is None: entire repository download (always ZIP)
        # - URL ends with .zip: server indicates it's a ZIP file
        # - is_directory explicitly set: force ZIP handling for directories
        is_zip = path is None or download_url.endswith('.zip') or is_directory

        if is_zip:
            # For directory downloads, use a temp file for the ZIP in system temp directory
            # Make sure it's not in the output directory to avoid confusion
            import tempfile
            temp_dir = tempfile.gettempdir()
            temp_file = tempfile.NamedTemporaryFile(suffix='.zip', delete=False, dir=temp_dir)
            download_path = Path(temp_file.name)
            temp_file.close()
        else:
            # For regular files, download directly to output location
            if path:
                filename = Path(path).name
            else:
                filename = f"repository_{repository_id}"
            download_path = output_dir / filename

        try:
            # Use a completely clean client for presigned URLs to avoid authentication conflicts
            if "X-Amz-Algorithm" in download_url:
                # Create a new, clean client for presigned URLs
                # Use longer timeout for large files/folders (10 minutes)
                with httpx.Client(timeout=httpx.Timeout(600.0, connect=30.0)) as clean_client:
                    with clean_client.stream("GET", download_url) as response:
                        response.raise_for_status()
                        total_size = int(response.headers.get("Content-Length", 0))

                        with open(download_path, "wb") as f:
                            if show_progress and total_size > 0:
                                desc = "Downloading ZIP" if is_zip else Path(path).name if path else "Download"
                                with tqdm(
                                    total=total_size,
                                    unit="B",
                                    unit_scale=True,
                                    desc=desc
                                ) as pbar:
                                    for chunk in response.iter_bytes(chunk_size=self.config.chunk_size):
                                        if chunk:  # Only write non-empty chunks
                                            f.write(chunk)
                                            pbar.update(len(chunk))
                                    f.flush()  # Ensure all data is written
                            else:
                                for chunk in response.iter_bytes(chunk_size=self.config.chunk_size):
                                    if chunk:  # Only write non-empty chunks
                                        f.write(chunk)
                                f.flush()  # Ensure all data is written
            else:
                # Use the existing authenticated client for regular API URLs
                with self.client.stream("GET", download_url) as response:
                    response.raise_for_status()
                    total_size = int(response.headers.get("Content-Length", 0))

                    with open(download_path, "wb") as f:
                        if show_progress and total_size > 0:
                            desc = "Downloading ZIP" if is_zip else Path(path).name if path else "Download"
                            with tqdm(
                                total=total_size,
                                unit="B",
                                unit_scale=True,
                                desc=desc
                            ) as pbar:
                                for chunk in response.iter_bytes(chunk_size=self.config.chunk_size):
                                    if chunk:  # Only write non-empty chunks
                                        f.write(chunk)
                                        pbar.update(len(chunk))
                                f.flush()  # Ensure all data is written
                        else:
                            for chunk in response.iter_bytes(chunk_size=self.config.chunk_size):
                                if chunk:  # Only write non-empty chunks
                                    f.write(chunk)
                            f.flush()  # Ensure all data is written

            # If it's a ZIP file (directory download), extract it
            if is_zip:
                try:
                    with zipfile.ZipFile(download_path, 'r') as zip_ref:
                        # List all files in the ZIP
                        zip_contents = zip_ref.namelist()

                        # Filter out checksum files and find the main directory
                        actual_files = [f for f in zip_contents if not f.endswith('.sha256')]

                        if actual_files:
                            # Extract only non-checksum files
                            for file in actual_files:
                                zip_ref.extract(file, output_dir)

                            # If path was specified, return the extracted directory
                            if path:
                                extracted_path = output_dir / Path(path).name
                                if extracted_path.exists():
                                    return extracted_path

                            # Otherwise, find the top-level directory that was extracted
                            top_dirs = set()
                            for file in actual_files:
                                parts = Path(file).parts
                                if parts:
                                    top_dirs.add(parts[0])

                            if len(top_dirs) == 1:
                                return output_dir / list(top_dirs)[0]
                            else:
                                return output_dir
                        else:
                            # If no files found, just return the output directory
                            return output_dir
                except zipfile.BadZipFile:
                    # If ZIP is corrupted, return the downloaded file as-is
                    return download_path
                finally:
                    # Clean up the temporary ZIP file - more aggressive cleanup
                    try:
                        if download_path and download_path.exists():
                            # Try to close any open file handles first
                            import gc
                            gc.collect()

                            # Now delete the file
                            download_path.unlink()

                            # Verify it's actually deleted
                            if download_path.exists():
                                # If still exists, try with force
                                import os
                                os.remove(str(download_path))
                    except Exception as e:
                        # Log the error but don't fail
                        print(f"Warning: Could not delete temporary ZIP file {download_path}: {e}")
            else:
                return download_path

        except Exception as e:
            # Clean up temp file on error
            if is_zip and download_path.exists():
                try:
                    download_path.unlink()
                except Exception:
                    pass  # Ignore cleanup errors
            raise DownloadError(f"Failed to download file: {e}")

    def get_batch_download_info(
        self,
        repository_id: int,
        paths: List[str]
    ) -> List[FileDownloadInfo]:
        """Get download information for multiple files."""
        try:
            response = self.client.post(
                f"/repositories/{repository_id}/download-list",
                json={"paths": paths}
            )
            response.raise_for_status()
            data = response.json()

            return [
                FileDownloadInfo(**item) for item in data.get("items", [])
            ]
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Invalid or expired API token")
            raise ApiError(f"Failed to get batch download info: {e}")

    async def download_batch(
        self,
        repository_id: int,
        paths: List[str],
        output_dir: Optional[Path] = None,
        show_progress: bool = True
    ) -> List[Path]:
        """Download multiple files in batch."""
        download_infos = self.get_batch_download_info(repository_id, paths)
        output_dir = output_dir or self.config.download_dir
        output_dir.mkdir(parents=True, exist_ok=True)

        downloaded_files = []

        async with httpx.AsyncClient() as client:
            tasks = []
            for info in download_infos:
                if info.type == "file":
                    task = self._async_download_file(
                        client,
                        info.presigned_url,
                        output_dir / info.name,
                        show_progress
                    )
                    tasks.append(task)

            downloaded_files = await asyncio.gather(*tasks, return_exceptions=True)

        successful_downloads = [f for f in downloaded_files if isinstance(f, Path)]
        return successful_downloads

    async def _async_download_file(
        self,
        client: httpx.AsyncClient,
        url: str,
        output_path: Path,
        show_progress: bool = True
    ) -> Path:
        """Async helper for downloading a single file."""
        try:
            response = await client.get(url)
            response.raise_for_status()
            output_path.write_bytes(response.content)
            return output_path
        except Exception as e:
            raise DownloadError(f"Failed to download {output_path.name}: {e}")

    def upload_file(
        self,
        repository_id: int,
        file_path: Path,
        remote_path: str = "",
        show_progress: bool = True
    ) -> Dict:
        """Upload a file to dataset (repository)."""
        # Convert to Path if string
        if isinstance(file_path, str):
            file_path = Path(file_path)

        if not file_path.exists():
            raise UploadError(f"File not found: {file_path}")

        try:
            with open(file_path, "rb") as f:
                files = {"file": (file_path.name, f)}
                # Always include path parameter, even if empty
                data = {"path": remote_path}

                # Debug logging to file
                with open("/tmp/upload_debug.log", "a") as debug_file:
                    debug_file.write(f"[CLIENT] Uploading file: {file_path.name}\n")
                    debug_file.write(f"[CLIENT] remote_path: '{remote_path}'\n")
                    debug_file.write(f"[CLIENT] data: {data}\n")
                    debug_file.write("===\n")

                if show_progress:
                    file_size = file_path.stat().st_size
                    with tqdm(total=file_size, unit="B", unit_scale=True, desc=file_path.name) as pbar:
                        response = self.client.post(
                            f"/repositories/{repository_id}/upload",
                            files=files,
                            data=data
                        )
                        pbar.update(file_size)
                else:
                    response = self.client.post(
                        f"/repositories/{repository_id}/upload",
                        files=files,
                        data=data
                    )

            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Invalid or expired API token")
            raise UploadError(f"Failed to upload file: {e}")