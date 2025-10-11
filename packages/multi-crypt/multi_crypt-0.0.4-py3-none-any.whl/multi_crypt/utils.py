"""Various helper functions"""
from pkgutil import walk_packages
from importlib import import_module
import pkgutil
import os
import sys
import importlib


def to_bytes(
    data: bytes | bytearray | str, variable_name: str = "Value"
) -> bytes:
    """Convert the input data from bytes or hex-string to bytes.

    Raises an error if it has the wrong type.

    Args:
        data: the data to convert
        variable_name: for error message
    """

    if isinstance(data, bytes):
        return data
    if isinstance(data, bytearray):
        return bytes(data)
    if isinstance(data, str):
        return bytes.fromhex(data)
    raise ValueError((
        f"{variable_name} must be of type bytes, bytes, or str, not "
        f"{type(data)}"
    ))


def load_module_from_path(path: str):
    """Load a python module from a file or a folder.
    Args:
        path (str): the path of the module file or folder
    Returns:
        module: the imported module
    """
    module_name = os.path.basename(path).strip(".py")
    if os.path.isdir(path):
        path = os.path.join(path, '__init__.py')
    spec = importlib.util.spec_from_file_location(
        module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def load_modules_from_package(package):
    """Given a package, imports all modules in that package.
    Args:
        package (module): the already imported package whose modules need to be imported
    Returns:
        dict: a dictionary of the imported modules
    """
    modules = dict()
    # load all cryptographic family modules from the algorithms folder
    for loader, module_name, is_pkg in walk_packages(path=package.__path__):
        module = import_module(f"{package.__name__}.{module_name}")
        modules.update({module_name: module})


def list_submodules(package_name):
    # Use pkgutil.walk_packages to get an iterator of submodule information
    submodules = pkgutil.walk_packages(path=__import__(
        package_name).__path__, prefix=package_name + '.')

    # Print the submodule names
    for loader, name, is_pkg in submodules:
        print(name)
    return [name for loader, name, is_pkg in submodules]
