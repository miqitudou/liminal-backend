from datetime import datetime

from fastapi import UploadFile
from qcloud_cos import CosConfig, CosS3Client

from app.core.config import settings
from app.core.exceptions import AppException


def upload_image(file: UploadFile) -> dict:
    if not all(
        [
            settings.cos_secret_id,
            settings.cos_secret_key,
            settings.cos_region,
            settings.cos_bucket,
        ]
    ):
        raise AppException(code=50002, message="腾讯云 COS 配置缺失")

    ext = ""
    if file.filename and "." in file.filename:
        ext = "." + file.filename.rsplit(".", 1)[-1]

    key = f"liminal/{datetime.now().strftime('%Y%m%d')}/{datetime.now().strftime('%H%M%S%f')}{ext}"
    config = CosConfig(
        Region=settings.cos_region,
        SecretId=settings.cos_secret_id,
        SecretKey=settings.cos_secret_key,
    )
    client = CosS3Client(config)
    client.put_object(
        Bucket=settings.cos_bucket,
        Body=file.file,
        Key=key,
    )

    file_url = (
        f"{settings.cos_domain.rstrip('/')}/{key}"
        if settings.cos_domain
        else f"https://{settings.cos_bucket}.cos.{settings.cos_region}.myqcloud.com/{key}"
    )

    return {
        "file_name": file.filename or key,
        "file_url": file_url,
        "file_key": key,
    }
