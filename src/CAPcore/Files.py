import gzip
import logging
import re
from hashlib import file_digest, sha256

import yaml

from .Misc import getUTC
from .Web import DownloadedPage

DEFAULTENCODING = "utf-8"


def readFile(filename: str, encoding: str = DEFAULTENCODING) -> DownloadedPage:
    if filename.endswith(".gz"):
        with gzip.open(filename, "rt") as handin:
            read_data = handin.read()
            resData = read_data
    else:
        with open(filename, "r", encoding=encoding) as handin:
            read_data = handin.read()
            resData = ''.join(read_data)

    return DownloadedPage(source=filename, data=resData, timestamp=getUTC())


def loadYAML(filename: str, encoding: str = DEFAULTENCODING):
    with open(filename, "r", encoding=encoding) as file:
        inHash = yaml.safe_load(file)

    return inHash


def saveYAML(data, filename: str, encoding: str = DEFAULTENCODING):
    with open(filename, "w", encoding=encoding) as file:
        yaml.safe_dump(data, file, indent=2, sort_keys=True)


def sha256sum(filename):
    with open(filename, 'rb', buffering=0) as f:
        return file_digest(f, 'sha256').hexdigest()


# From: https://stackoverflow.com/a/44873382
# Digest method must be in sync with function shaData
def shaFile(filename):
    with open(filename, 'rb', buffering=0) as f:
        return file_digest(f, 'sha256').hexdigest()


# Digest method must be in sync with function shaFile
def shaData(data):
    result = sha256(data, usedforsecurity=False).hexdigest()

    return result


def extensionFromType(dataType: str):
    if dataType in {'image/png'}:
        return 'png'
    if dataType in {'image/jpeg'}:
        return 'jpg'
    if dataType in {'image/gif'}:
        return 'gif'
    logging.error("Unknown type '%s'", dataType)
    raise TypeError(f"Unknown type {dataType}")


# From https://stackoverflow.com/a/55101759
def getSaneFilenameStr(inStr: str) -> str:
    validchars = "-_.()"
    out = ""
    for c in inStr.strip():
        if str.isalpha(c) or str.isdigit(c) or (c in validchars):
            out += c
        else:
            out += "_"

    result = re.sub(r'__+', r'_', out).strip('_')

    return result
