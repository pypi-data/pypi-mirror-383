import os
from datetime import datetime, timedelta, timezone
from typing import Optional, BinaryIO, Tuple

from azure.storage.blob import BlobServiceClient, BlobSasPermissions, generate_blob_sas
from fastapi import UploadFile

from loguru import logger


class AzureBlobService:
    """Minimal Azure Blob helper with SAS URL generation."""

    def __init__(self) -> None:
        self.container_name = os.getenv("AZURE_BLOB_CONTAINER", "uploads")
        self.connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        self.account_key = os.getenv("AZURE_STORAGE_ACCOUNT_KEY")
        self.sas_token = os.getenv("AZURE_SAS_TOKEN")
        self.base_blob_url = os.getenv("AZURE_BLOB_URL")

        if not self.connection_string:
            logger.warning(
                "Azure Storage connection string not configured; blob operations will fail."
            )

    def _get_blob_service(self) -> BlobServiceClient:
        if not self.connection_string:
            raise RuntimeError("AZURE_STORAGE_CONNECTION_STRING not configured")
        clean = self.connection_string.strip().strip('"').strip("'")
        return BlobServiceClient.from_connection_string(clean)

    def _parse_account_from_connection_string(self) -> Tuple[Optional[str], Optional[str]]:
        if not self.connection_string:
            return None, None
        try:
            clean = self.connection_string.strip().strip('"').strip("'")
            parts = dict(
                seg.split("=", 1) for seg in clean.split(";") if "=" in seg
            )
            account_name = parts.get("AccountName")
            account_key = parts.get("AccountKey") or self.account_key
            return account_name, account_key
        except Exception:
            return None, None

    def _ensure_container(self, client: BlobServiceClient) -> None:
        try:
            client.create_container(self.container_name)
        except Exception:
            pass

    def _generate_sas_url(self, blob_name: str, expiry_days: int = 730) -> str:
        account_name, account_key = self._parse_account_from_connection_string()
        if not account_name:
            try:
                client = self._get_blob_service()
                account_name = getattr(client, "account_name", None)
            except Exception:
                account_name = None

        account_key = account_key or self.account_key
        if not account_name or not account_key:
            raise RuntimeError("Azure Storage account name/key not configured; cannot generate SAS")

        start_time = datetime.now(timezone.utc) - timedelta(minutes=5)
        expiry_time = start_time + timedelta(days=expiry_days)
        sas = generate_blob_sas(
            account_name=account_name,
            container_name=self.container_name,
            blob_name=blob_name,
            account_key=account_key,
            permission=BlobSasPermissions(read=True),
            start=start_time,
            expiry=expiry_time,
            protocol="https",
        )

        if self.base_blob_url:
            base_url = self.base_blob_url.strip().strip('"').strip("'").rstrip("/")
            return f"{base_url}/{blob_name}?{sas}"
        return f"https://{account_name}.blob.core.windows.net/{self.container_name}/{blob_name}?{sas}"

    async def upload_file(self, file: UploadFile, blob_path: str) -> Optional[str]:
        if not self.connection_string:
            logger.error("Azure Storage connection string not configured")
            return None
        try:
            client = self._get_blob_service()
            self._ensure_container(client)
            container = client.get_container_client(self.container_name)
            content = await file.read()
            blob_client = container.get_blob_client(blob_path)
            blob_client.upload_blob(content, overwrite=True, content_type=file.content_type or "application/octet-stream")
            return self._generate_sas_url(blob_path)
        except Exception as e:
            logger.error(f"Failed to upload file {file.filename}: {e}")
            return None

    async def upload_stream(self, stream: BinaryIO, blob_path: str, content_type: str = "application/octet-stream") -> Optional[str]:
        if not self.connection_string:
            logger.error("Azure Storage connection string not configured")
            return None
        try:
            client = self._get_blob_service()
            self._ensure_container(client)
            container = client.get_container_client(self.container_name)
            blob_client = container.get_blob_client(blob_path)
            blob_client.upload_blob(stream, overwrite=True, content_type=content_type)
            return self._generate_sas_url(blob_path)
        except Exception as e:
            logger.error(f"Failed to upload stream to {blob_path}: {e}")
            return None

