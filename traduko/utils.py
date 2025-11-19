import io
import json
import tarfile
from contextlib import contextmanager
from datetime import datetime

UnknownJsonData = str | dict[str, str]


def ensure_json(data: UnknownJsonData) -> str:
    if isinstance(data, dict):
        data = json.dumps(data, ensure_ascii=False, indent=2)
    return data


@contextmanager
def in_memory_bytes(initial_bytes=b""):
    buffer = io.BytesIO(initial_bytes)
    try:
        yield buffer
    finally:
        buffer.seek(0)


def as_tar_file(name: str, data: bytes) -> tuple[tarfile.TarInfo, io.BytesIO]:
    tar_info = tarfile.TarInfo(name)
    tar_info.size = len(data)
    tar_info.mtime = int(datetime.now().timestamp())
    return tar_info, io.BytesIO(data)
