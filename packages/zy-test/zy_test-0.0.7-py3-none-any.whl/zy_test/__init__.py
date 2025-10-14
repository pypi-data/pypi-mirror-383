import pkgutil
import importlib
import sys


# Dynamically import all submodules and subpackages
def _import_submodules(package_name):
    package = sys.modules[package_name]
    package_path = package.__path__

    for _, module_name, is_pkg in pkgutil.walk_packages(package_path, package_name + '.'):
        importlib.import_module(module_name)

        if not is_pkg:
            # Add the module name to the __all__ list
            __all__.append(module_name.split('.')[-1])


# Initialize the __all__ list
__all__ = []

# Import all submodules and subpackages
_import_submodules(__name__)
