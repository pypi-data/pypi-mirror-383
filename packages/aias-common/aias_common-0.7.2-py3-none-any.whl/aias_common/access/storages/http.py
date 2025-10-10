import time
from urllib.parse import urlparse

from aias_common.access.configuration import AccessType, HttpStorageConfiguration
from aias_common.access.file import File
from aias_common.access.storages.abstract import AbstractStorage
from aias_common.access.storages.utils import (requests_exists, requests_get,
                                               requests_head)


class HttpStorage(AbstractStorage):

    def is_path_authorized(self, href: str, action: AccessType) -> bool:
        paths = self.get_authorized_pathes(href, action)
        path = urlparse(href).path
        return any(list(map(lambda p: path.startswith(p.removesuffix("/") + "/"), paths)))

    def to_string(self) -> str:
        return "{} storage at {}".format(self.get_configuration().type, self.get_configuration().domain)

    def get_configuration(self) -> HttpStorageConfiguration:
        assert isinstance(self.storage_configuration, HttpStorageConfiguration)
        return self.storage_configuration

    def get_storage_parameters(self) -> dict:
        return {"headers": self.get_configuration().headers}

    def supports(self, href: str):
        scheme = urlparse(href).scheme
        netloc = urlparse(href).netloc
        return scheme == self.get_configuration().type and netloc == self.get_configuration().domain

    def exists(self, href: str):
        return requests_exists(href, self.get_configuration().headers)

    def get_rasterio_session(self, href):
        # Might not work
        return {}

    def pull(self, href: str, dst: str):
        super().pull(href, dst)
        requests_get(href, dst, self.get_configuration().headers)

    def push(self, href: str, dst: str, content_type: str | None = None):
        super().push(href, dst)
        raise NotImplementedError("'push' method is not available for http storage")

    def is_file(self, href: str):
        return self.exists(href)

    def is_dir(self, href: str):
        return False

    def get_file_size(self, href: str):
        r = requests_head(href, self.get_configuration().headers)
        return r.headers.get("Content-Length")

    def listdir(self, href: str) -> list[File]:
        raise NotImplementedError(f"It is not possible to list the content of a directory with {self.get_configuration().type} protocol")

    def get_last_modification_time(self, href: str) -> float | None:
        r = requests_head(href, self.get_configuration().headers)
        if r.headers.get("Last-Modified"):
            return time.mktime(time.strptime(r.headers.get("Last-Modified"), "%a, %d %b %Y %H:%M:%S %Z"))
        return None

    def get_creation_time(self, href: str) -> float | None:
        # There is no difference in HTTP(S) between last update and creation date
        return self.get_last_modification_time(href)

    def makedir(self, href: str, strict=False):
        if strict:
            raise NotImplementedError(f"It is not possible to create the folder with {self.get_configuration().type} protocol")

    def clean(self, href: str):
        raise NotImplementedError(f"It is not possible to delete a file with {self.get_configuration().type} protocol")

    def get_gdal_stream_options(self):
        params = {}
        for (k, v) in self.get_configuration().headers.items():
            params[f"header.{k}"] = v

        return params

    def gdal_transform_href_vsi(self, href: str) -> str:
        return "/vsicurl/" + href
