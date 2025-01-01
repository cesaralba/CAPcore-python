"""
Python specific functions
"""
import sys
from importlib import import_module


def loadModule(moduleName: str, classLocation: str):
    fullModName = f"{classLocation}.{moduleName}"

    if fullModName not in sys.modules:
        import_module(fullModName, classLocation)

    return fullModName, sys.modules[fullModName]
