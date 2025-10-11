<h1><img src="logo.svg" width="200" alt="getargv"></h1>

[![Python package](https://github.com/getargv/getargv.py/actions/workflows/python-package.yml/badge.svg)](https://github.com/getargv/getargv.py/actions/workflows/python-package.yml)

This module uses libgetargv to obtain binary string representations of the arguments of other processes on macOS.

## Motivation

On macOS you must use the KERN_PROCARGS2 sysctl to obtain other proc's args, however the returned representation is badly documented and a naive approach doesn't deal with leading empty args. libgetargv parses the results of the sysctl correctly, and this module provides Python bindings to libgetargv.

## Installation

Install the module with pip by executing:

    $ pip install getargv

## Usage

```python
import os
import getargv
getargv.as_bytes(os.getpid()) #=> b'arg0\x00arg1\x00'
getargv.as_list(os.getpid()) #=> [b'arg0',b'arg1']
```

## Development

After checking out the repo, run `python setup.py build`. Then run `python setup.py install`. Then, run `python test.py` to run the tests. You can also run `python -i load.py` for an interactive prompt that will allow you to experiment. Python code goes in the file `src/getargv/__init__.py`, C code goes in the file `src/getargv/getargvmodule.c`.

To install this module onto your local machine, run `python setup.py build && python setup.py install`. To release a new version, update the version number in `pyproject.toml`, and then run `make upload-production`, which will create a git tag for the version, push git commits and the created tag, and push the `.whl` file to [pypi.org](https://pypi.org).

## Contributing

Bug reports and pull requests are welcome on GitHub at https://github.com/getargv/getargv.py.

## License

The module is available as open source under the terms of the [BSD 3-clause License](https://opensource.org/licenses/BSD-3-Clause).
