# Python code for getargv module

"""Obtain binary string representations of the arguments of other PIDs.

On macOS you must use the KERN_PROCARGS2 sysctl to obtain other procs' args,
however the returned representation is badly documented and a naive approach
doesn't deal with leading empty args. libgetargv parses the results of the
sysctl correctly, and this module provides Python bindings to libgetargv.

Classes:

    error Error class for this package

Functions:

    as_bytes(pid, skip, nuls) -> bytes
    as_string(pid, encoding, skip, nuls) -> str
    as_list(pid) -> list[bytes]
    as_string_list(pid, encoding) -> list[str]

Misc variables:

    __version__ The package version
"""

import sys
from typing import List
if sys.version_info >= (3, 8):
    from importlib import metadata
else:
    import importlib_metadata as metadata

if sys.platform != 'darwin':
    from warnings import warn
    warn("only macOS is supported")

from _getargv import as_bytes, as_list

# pyright: reportUnknownMemberType=false
__version__: str = metadata.version('getargv')

def as_string(pid: int, encoding: str, skip: int = 0, nuls: bool = False) -> str:
    """Returns the arguments of a pid as a string decoded using specified encoding.

            Parameters:
                    pid (int): An integer PID
                    encoding (str): A string encoding
                    skip (int): How many leading arguments to skip past
                    nuls (bool): Whether to convert nuls to spaces for human readability

            Returns:
                    args (str): Binary string of the PID's args
    """
    return as_bytes(pid, skip, nuls).decode(encoding)

def as_string_list(pid: int, encoding: str) -> List[str]:
    """Returns the arguments of a pid as an list of strings decoded using specified encoding.

            Parameters:
                    pid (int): An integer PID
                    encoding (str): A string encoding

            Returns:
                    args (list[bytes]): List of the PID's args as binary strings
    """
    return [b.decode(encoding) for b in as_list(pid)]

__all__ = [
    "__version__",
    "as_bytes",
    "as_string",
    "as_list",
    "as_string_list"
]
