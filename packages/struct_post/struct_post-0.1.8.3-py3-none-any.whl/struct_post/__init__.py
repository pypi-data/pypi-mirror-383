# struct_post/__init__.py

from importlib import metadata

__version__ = metadata.version("struct_post")

from . import coupon, beam
from .read_lvm_file import read_lvm_file
