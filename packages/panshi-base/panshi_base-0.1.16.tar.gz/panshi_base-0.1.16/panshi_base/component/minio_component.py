import datetime
import os
import uuid

try:
    import minio
except ImportError:
    raise ValueError("minio is not installed. Please install it with `poetry add minio`")

from loguru import logger


class MinioComponent:
    def __init__(self, endpoint: str, access_key: str, secret_key: str, bucket_name: str):
        self.minio_client = minio.Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=False
        )
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket_name = bucket_name
        if not self.minio_client.bucket_exists(self.bucket_name):
            self.minio_client.make_bucket(self.bucket_name)
        logger.info("minio连接成功")

    @staticmethod
    def get_minio_path(file_path: str) -> str:
        now = datetime.datetime.now()
        year = now.year
        month = now.month
        day = now.day
        file_extension = os.path.splitext(file_path)[1][1:].lower()
        return str(year) + "/" + str(month) + "/" + str(day) + "/" + str(uuid.uuid4()) + "." + file_extension

    def upload_file(self, file_path: str) -> tuple[str, str]:
        minio_file_path = self.get_minio_path(file_path)
        minio_file_url = None
        try:
            with open(file_path, 'rb') as file_data:
                file_stat = os.stat(file_path)
                self.minio_client.put_object(self.bucket_name, minio_file_path, file_data, file_stat.st_size)
            logger.debug(f"{file_path}文件上传成功")
            minio_file_url = "http://" + self.endpoint + "/" + self.bucket_name + "/" + minio_file_path
        except Exception as err:
            logger.error(err)
        return minio_file_path, minio_file_url

    def download_file(self, minio_file_path: str, save_file_path: str) -> bool:
        try:
            data = self.minio_client.get_object(self.bucket_name, minio_file_path)
            with open(save_file_path, 'wb') as file_data:
                for d in data.stream(32 * 1024):
                    file_data.write(d)
            logger.debug(f"下载文件成功，保存在{save_file_path}中")
            return True
        except Exception as err:
            logger.error(err)
        return False

    def remove_file(self, minio_file_path: str) -> bool:
        try:
            self.minio_client.remove_object(self.bucket_name, minio_file_path)
        except Exception as err:
            logger.error(err)
        return False
