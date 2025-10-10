"""Async SFTP uploader with parallel uploads and retry logic."""

import asyncio
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

import asyncssh
from asyncssh import SFTPClient


@dataclass
class UploadStats:
    """Statistics for upload operation."""

    total_files: int = 0
    successful: int = 0
    failed: int = 0
    skipped: int = 0
    duration: float = 0.0
    failed_files: dict[str, str] = field(default_factory=dict)


class SFTPUploader:
    """Async SFTP uploader with parallel uploads and retry logic."""

    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: Optional[str] = None,
        key_file: Optional[str] = None,
        max_workers: int = 10,
        max_retries: int = 3,
    ):
        """
        Initialize SFTP uploader.

        Args:
            host: SFTP server hostname
            port: SFTP server port
            username: SFTP username
            password: SFTP password (optional if using key_file)
            key_file: Path to SSH private key file (optional if using password)
            max_workers: Maximum number of parallel uploads
            max_retries: Maximum number of retries per file
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.key_file = key_file
        self.max_workers = max_workers
        self.max_retries = max_retries
        self._semaphore = asyncio.Semaphore(max_workers)

    async def _create_connection(self) -> asyncssh.SSHClientConnection:
        """Create an SSH connection to the SFTP server."""
        connect_kwargs = {
            "host": self.host,
            "port": self.port,
            "username": self.username,
            "known_hosts": None,  # Disable host key checking (use with caution)
        }

        if self.key_file:
            connect_kwargs["client_keys"] = [self.key_file]
        if self.password:
            connect_kwargs["password"] = self.password

        conn = await asyncssh.connect(**connect_kwargs)
        return conn

    async def _ensure_remote_dir(
        self, sftp: SFTPClient, remote_path: str
    ) -> None:
        """
        Ensure remote directory exists, creating it if necessary.

        Args:
            sftp: SFTP client
            remote_path: Remote directory path
        """
        # Normalize path
        remote_path = remote_path.replace("\\", "/")
        parts = [p for p in remote_path.split("/") if p]

        # Build path incrementally
        current_path = "/" if remote_path.startswith("/") else ""
        for part in parts:
            current_path += part if current_path.endswith("/") else f"/{part}"
            try:
                await sftp.stat(current_path)
            except (asyncssh.SFTPError, OSError):
                # Directory doesn't exist, create it
                try:
                    await sftp.mkdir(current_path)
                except (asyncssh.SFTPError, OSError):
                    # Ignore if directory was created by another worker
                    pass

    async def _upload_file(
        self,
        local_path: str,
        remote_path: str,
        conn: asyncssh.SSHClientConnection,
        retries: int = 0,
    ) -> tuple[str, bool, Optional[str]]:
        """
        Upload a single file with retry logic.

        Args:
            local_path: Local file path
            remote_path: Remote file path
            conn: SSH connection
            retries: Current retry attempt

        Returns:
            Tuple of (file_path, success, error_message)
        """
        async with self._semaphore:
            try:
                async with conn.start_sftp_client() as sftp:
                    # Ensure remote directory exists
                    remote_dir = str(Path(remote_path).parent)
                    await self._ensure_remote_dir(sftp, remote_dir)

                    # Upload file
                    await sftp.put(local_path, remote_path)
                    return (local_path, True, None)

            except Exception as e:
                error_msg = str(e)

                # Retry logic
                if retries < self.max_retries:
                    # Exponential backoff
                    wait_time = 2 ** retries
                    await asyncio.sleep(wait_time)
                    return await self._upload_file(
                        local_path, remote_path, conn, retries + 1
                    )

                # Max retries exceeded
                return (local_path, False, error_msg)

    async def upload_folder(
        self,
        local_folder: str,
        remote_folder: str,
        recursive: bool = True,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> UploadStats:
        """
        Upload a folder to SFTP server with parallel uploads.

        Args:
            local_folder: Local folder path
            remote_folder: Remote folder path
            recursive: Whether to upload recursively
            progress_callback: Optional callback for progress updates (current, total)

        Returns:
            UploadStats object with upload statistics
        """
        start_time = time.time()
        stats = UploadStats()

        # Collect all files to upload
        local_path = Path(local_folder)
        if recursive:
            files = [f for f in local_path.rglob("*") if f.is_file()]
        else:
            files = [f for f in local_path.iterdir() if f.is_file()]

        stats.total_files = len(files)

        if stats.total_files == 0:
            stats.duration = time.time() - start_time
            return stats

        # Create connection pool (one connection per worker)
        connections = []
        try:
            # Create SSH connections
            for _ in range(min(self.max_workers, stats.total_files)):
                conn = await self._create_connection()
                connections.append(conn)

            # Create upload tasks
            tasks = []
            for i, file_path in enumerate(files):
                # Calculate relative path and remote path
                rel_path = file_path.relative_to(local_path)
                remote_path = f"{remote_folder}/{str(rel_path).replace(chr(92), '/')}"

                # Use connection in round-robin fashion
                conn = connections[i % len(connections)]

                # Create upload task
                task = self._upload_file(str(file_path), remote_path, conn)
                tasks.append(task)

            # Execute uploads in parallel with progress tracking
            completed = 0
            for coro in asyncio.as_completed(tasks):
                local_file, success, error = await coro
                completed += 1

                if success:
                    stats.successful += 1
                else:
                    stats.failed += 1
                    stats.failed_files[local_file] = error or "Unknown error"

                # Update progress
                if progress_callback:
                    progress_callback(completed, stats.total_files)

        finally:
            # Close all connections
            for conn in connections:
                conn.close()
                await conn.wait_closed()

        stats.duration = time.time() - start_time
        return stats

