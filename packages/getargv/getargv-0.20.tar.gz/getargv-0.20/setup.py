from setuptools import setup, Extension
from distutils.ccompiler import new_compiler
from platform import processor
from sysconfig import get_config_var
from os import environ, path
from typing import Any, TypedDict, Literal, cast, Union, List, Dict
import subprocess
import sys
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

# debug by setting DISTUTILS_DEBUG env var in shell to anything

assert sys.platform == "darwin"

encoding:str = 'UTF-8'

def get_macos_target(lib_dirs:List[str], lib_name:str)->str:
    default = get_config_var('MACOSX_DEPLOYMENT_TARGET')
    compiler = new_compiler()
    lib_file = compiler.find_library_file(lib_dirs,lib_name)
    try:
        output = subprocess.check_output('vtool -show-build {}'.format(lib_file), shell=True)
        return next((l for l in output.splitlines() if b'minos' in l), default).split().pop().decode(encoding,errors='ignore')
    except subprocess.CalledProcessError:
        return default

def homebrew_prefix(inpath:str, package:str)->str:
    if processor() == 'arm':
        hb_path = "/opt/homebrew"
    else:
        hb_path = "/usr/local"
    if path.exists(path.join(hb_path,inpath)):
        return path.join(hb_path, inpath)
    else:
        return path.join(hb_path, "opt", package, inpath)

def macports_prefix(inpath:str)->str:
    return path.join("/opt/local/", inpath)

def platform_prefix(inpath:str, package:str)->str:
    if path.exists("/opt/local/bin/port"):
        return macports_prefix(inpath)
    elif path.exists("/opt/homebrew/bin/brew") or path.exists("/usr/local/bin/brew"):
        return homebrew_prefix(inpath, package)
    else:
        return (environ.get("PREFIX") or "/").join(inpath)

class Params(TypedDict):
    libraries: List[str]
    include_dirs: List[str]
    library_dirs: List[str]

def pkgconfig(package:str)-> Params:
    kw: Params = {'include_dirs':[], 'library_dirs':[], 'libraries':[]}
    flag_map = {'-I': 'include_dirs', '-L': 'library_dirs', '-l': 'libraries'}
    try:
        output = subprocess.check_output('pkg-config --cflags --libs {}'.format(package),shell=True)
        for token in output.strip().split():
            key: Union[str, None] = flag_map.get(token[:2].decode(encoding,errors='ignore'))
            assert key is not None
            kw[cast(Literal['include_dirs','library_dirs','libraries'],key)].append(token[2:].decode(encoding))
    finally:
        return kw

try:
    dev_path:str = subprocess.check_output('xcode-select -p',shell=True).strip().decode(encoding,errors='ignore')
except:
    raise Exception('''You must have either the CLT or Xcode installed to build extensions.
You can install the CLT with `xcode-select --install`, which is much smaller than the full Xcode.
''')

package_name:str = 'getargv'
kw: Params = pkgconfig(package_name)
kw['include_dirs'].append(platform_prefix('include', package_name))
kw['include_dirs'].append('{}/Library/Frameworks/Python3.framework/Headers'.format(dev_path))
kw['library_dirs'].append(platform_prefix('lib', package_name))
kw['libraries'].append(package_name)

environ["MACOSX_DEPLOYMENT_TARGET"] = get_macos_target(kw['library_dirs'],package_name)

with open("pyproject.toml", mode="rb") as fp:
    project: Dict[str, Any] = tomllib.load(fp)['project']
    config: Dict[str, Any] = project.copy()
    for k in project.keys():
        if k == 'authors':
            author: Dict[str, str] = config[k][0]
            config['author'] = author['name']
            config['author_email'] = author['email']
            del config[k]
        if k == 'urls':
            config['url'] = config[k]['Homepage']
            del config[k]
        if k == 'dependencies':
            config['install_requires'] = config[k]
            del config[k]
        if k in ['readme', 'requires-python', 'license-files']:
            del config[k]

if __name__ == "__main__":
    setup(
        ext_modules = [ Extension( "_getargv", sources = ['src/getargv/_getargvmodule.c'], **kw) ],
        **config
    )
