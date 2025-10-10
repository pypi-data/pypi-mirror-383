import os
from urllib.parse import urlparse, urlunparse

from aias_common.access.configuration import AccessType, S3StorageConfiguration
from aias_common.access.file import File
from aias_common.access.logger import Logger
from aias_common.access.storages.abstract import AbstractStorage
from fastapi_utilities import ttl_lru_cache
import aioboto3
from memory_profiler import profile

from aias_common.access.storages.path_helper import endslash, join_pathes, noslash

LOGGER = Logger.logger


class S3Storage(AbstractStorage):

    def is_path_authorized(self, href: str, action: AccessType) -> bool:
        paths = self.get_authorized_pathes(href, action)

        prefix = join_pathes(self.get_configuration().endpoint, self.get_configuration().bucket)
        h = endslash(noslash(href))
        return any(list(map(lambda p: h.startswith(endslash(join_pathes(prefix, p))), paths)))

    def to_string(self) -> str:
        return "object storage on bucket {} from {}".format(self.get_configuration().bucket, self.get_configuration().endpoint)

    def get_configuration(self) -> S3StorageConfiguration:
        assert isinstance(self.storage_configuration, S3StorageConfiguration)
        return self.storage_configuration

    def get_storage_parameters(self) -> dict:
        import boto3
        conf = self.get_configuration()
        if conf.is_anon_client:
            from botocore import UNSIGNED
            from botocore.client import Config

            client = boto3.client(
                "s3",
                region_name=conf.region,
                endpoint_url=conf.endpoint,
                config=Config(signature_version=UNSIGNED)
            )
        else:
            client = boto3.client(
                "s3",
                region_name=conf.region,
                endpoint_url=conf.endpoint,
                aws_access_key_id=conf.api_key.access_key,
                aws_secret_access_key=conf.api_key.secret_key,
            )

        return {"client": client}

    def __aioboto3_client(self):
        conf = self.get_configuration()
        if conf.is_anon_client:
            from botocore import UNSIGNED
            from botocore.client import Config
            session = aioboto3.Session()
            client = session.client(
                "s3",
                region_name=conf.region,
                endpoint_url=conf.endpoint,
                config=Config(signature_version=UNSIGNED)
            )
        else:
            session = aioboto3.Session()
            client = session.client(
                "s3",
                region_name=conf.region,
                endpoint_url=conf.endpoint,
                aws_access_key_id=conf.api_key.access_key,
                aws_secret_access_key=conf.api_key.secret_key,
            )
        return client

    def supports(self, href: str):
        scheme = urlparse(href).scheme
        netloc = urlparse(href).netloc
        path = urlparse(href).path
        if scheme == "s3":
            return netloc == self.get_configuration().bucket
        elif scheme == "http" or scheme == "https":
            return f"{scheme}://{netloc}" == self.get_configuration().endpoint and len(path.split("/")) > 1 and path.split("/")[1] == self.get_configuration().bucket
        return False

    def exists(self, href: str):
        return self.is_dir(href) or self.is_file(href)

    def get_rasterio_session(self, href: str):
        import rasterio.session

        params = {}

        if self.get_configuration().is_anon_client:
            params["session"] = rasterio.session.AWSSession(
                aws_unsigned=True,
                region_name=self.get_configuration().region,
                endpoint_url=self.get_configuration().endpoint
            )
        else:
            params["session"] = rasterio.session.AWSSession(
                aws_access_key_id=self.get_configuration().api_key.access_key,
                aws_secret_access_key=self.get_configuration().api_key.secret_key,
                region_name=self.get_configuration().region,
                endpoint_url=self.get_configuration().endpoint
            )

        return params

    def get_full_href(self, path: str):
        if self.get_configuration().endpoint:
            return join_pathes(self.get_configuration().endpoint, self.get_configuration().bucket, path)
        else:
            return "s3://" + join_pathes(self.get_configuration().bucket, path)

    def __get_href_key(self, href: str):
        return urlparse(href).path.removeprefix(f"/{self.get_configuration().bucket}").removeprefix("/").removesuffix("/") 

    def pull(self, href: str, dst: str):
        import botocore.client

        client: botocore.client.BaseClient = self.get_storage_parameters()["client"]

        obj = client.get_object(Bucket=self.get_configuration().bucket, Key=self.__get_href_key(href))
        with open(dst, "wb") as f:
            for chunk in obj['Body'].iter_chunks(50 * 1024):
                f.write(chunk)

    def push(self, href: str, dst: str, content_type: str | None = None):
        import botocore.client
        client: botocore.client.BaseClient = self.get_storage_parameters()["client"]
        extraArgs = {}
        if content_type:
            extraArgs["ContentType"] = content_type
        client.upload_file(href, Bucket=self.get_configuration().bucket, Key=self.__get_href_key(dst), ExtraArgs=extraArgs)

    @profile
    async def async_push_file_obj(self, file_obj, dst: str, content_type: str | None = None):
        """push source file like object on destination

        Args:
            file_obj: A source file like object (https://docs.python.org/3/glossary.html#term-file-object)
            dst (str): target destination for coping the content of file_obj
            content_type (str | None, optional): content type of the source file. Defaults to None.
        """
        extra_args = {}
        if content_type:
            extra_args["ContentType"] = content_type
        total = 0
        nb_calls = 0
        
        def log_progress(bytes_amount):
            nonlocal total
            nonlocal nb_calls
            total = total + bytes_amount
            if nb_calls % 10 != 0:
                LOGGER.debug(f"{total / 1000000} bytes transfered so far")
            nb_calls = nb_calls + 1

        async with self.__aioboto3_client() as s3:
            await s3.upload_fileobj(file_obj, Bucket=self.get_configuration().bucket, Key=self.__get_href_key(dst), ExtraArgs=extra_args, Callback=log_progress)
        
    @ttl_lru_cache(ttl=AbstractStorage.cache_tt, max_size=AbstractStorage.cache_size)
    def __head_object(self, href: str):
        conf = self.get_configuration()
        if self.__get_href_key(href):
            try:
                return self.get_storage_parameters()["client"].head_object(
                    Bucket=conf.bucket,
                    Key=self.__get_href_key(href))
            except:
                return None
        else:
            return None

    def is_file(self, href: str):
        import botocore.exceptions
        try:
            response = self.__head_object(href)
            return (response is not None) and response['ResponseMetadata']['HTTPStatusCode'] == 200
        except botocore.exceptions.ClientError:
            return False

    @ttl_lru_cache(ttl=AbstractStorage.cache_tt, max_size=AbstractStorage.cache_size)
    def __list_objects(self, href: str):
        conf = self.get_configuration()
        params = {
            "Bucket": conf.bucket,
            "Delimiter": "/",
            "MaxKeys": conf.max_objects
        }
        prefix = self.__get_href_key(href) + "/"
        if prefix != "/":
            params["Prefix"] = prefix
        return self.get_storage_parameters()["client"].list_objects_v2(**params)

    def is_dir(self, href: str) -> bool:
        objects = self.__list_objects(href)
        return (objects is not None) and (objects['KeyCount'] > 0 or len(objects.get('CommonPrefixes', [])) > 0)

    def get_file_size(self, href: str):
        response = self.__head_object(href)
        if response:
            return response['ContentLength']
        else:
            return None

    def __update_url__(self, source: str, path: str):
        url = urlparse(source)
        components = list(url[:])
        if len(components) == 5:
            components.append('')
        components[2] = os.path.join(self.get_configuration().bucket, path)
        return urlunparse(tuple(components))

    def listdir(self, href: str) -> list[File]:
        objects = self.__list_objects(href)
        files = []
        if objects.get("Contents"):
            files = list(map(lambda c: File(
                name=os.path.basename(c["Key"]),
                path=self.__update_url__(href, c["Key"]),
                is_dir=False,
                last_modification_date=c["LastModified"]), filter(lambda x: os.path.basename(x["Key"]), objects["Contents"])))
        dirs = []
        if objects.get("CommonPrefixes"):
            dirs = list(map(lambda d: File(
                name=os.path.basename(d["Prefix"].removesuffix("/")),
                path=self.__update_url__(href, d["Prefix"]),
                is_dir=True), objects["CommonPrefixes"]))
        return files + dirs

    def get_last_modification_time(self, href: str) -> float | None:
        import botocore.exceptions
        try:
            response = self.__head_object(href)
            if response:
                return response['LastModified'].timestamp()
            return None
        except botocore.exceptions.ClientError:
            return None
        except botocore.exceptions.ParamValidationError:  # key LastModified does not exists for root
            return None

    def get_creation_time(self, href: str) -> float | None:
        # There is no difference in s3 between last update and creation date
        return self.get_last_modification_time(href)

    def makedir(self, href: str, strict=False):
        if strict:
            raise PermissionError("Creating a folder on a remote storage is not permitted")

    def clean(self, href: str):
        import botocore.client
        client: botocore.client.BaseClient = self.get_storage_parameters()["client"]
        client.delete_object(Bucket=self.get_configuration().bucket, Key=self.__get_href_key(href))

    def get_gdal_stream_options(self):
        config = self.get_configuration()

        params = {
            "AWS_VIRTUAL_HOSTING": "FALSE",
            # Before GDAL 3.11, http and https should not be in the endpoint adress
            "AWS_S3_ENDPOINT": config.endpoint.removeprefix("http://").removeprefix("https://")  # NOSONAR
        }

        if config.region != "auto":
            params["AWS_DEFAULT_REGION"] = config.region
        if config.is_anon_client:
            params["AWS_NO_SIGN_REQUEST"] = "YES"
        else:
            params["AWS_NO_SIGN_REQUEST"] = "NO"
            params["AWS_SECRET_ACCESS_KEY"] = config.api_key.secret_key
            params["AWS_ACCESS_KEY_ID"] = config.api_key.access_key

        # Not needed after GDAL 3.11
        if config.endpoint.startswith("http://"):  # NOSONAR
            params["AWS_HTTPS"] = "FALSE"
        return params

    def gdal_transform_href_vsi(self, href: str) -> str:
        config = self.get_configuration()

        if urlparse(href).scheme == "s3":
            href = href.replace("s3://", "/vsis3/")
        else:
            href = href.replace(config.endpoint, "/vsis3")

        return href

    def get_matching_s3_objects(self, path: str, suffix: str = "", s3_client=None):

        prefix = noslash(urlparse(path).path.removeprefix("/" + self.get_configuration().bucket))
        LOGGER.debug("Search for objects in bucket %s with prefix %s and suffix %s", self.get_configuration().bucket, prefix, suffix)
        import botocore.client
        client: botocore.client.BaseClient = self.get_storage_parameters()["client"]
        paginator = client.get_paginator("list_objects_v2")

        kwargs = {'Bucket': self.get_configuration().bucket}
        kwargs["Prefix"] = prefix

        for page in paginator.paginate(**kwargs):
            try:
                contents = page["Contents"]
            except KeyError:
                break

            for obj in contents:
                key = obj["Key"]
                if key.endswith(suffix):
                    yield key

    def get_matching_s3_keys(self, prefix="", suffix=""):
        for obj in self.get_matching_s3_objects(prefix, suffix):
            yield obj["Key"]

