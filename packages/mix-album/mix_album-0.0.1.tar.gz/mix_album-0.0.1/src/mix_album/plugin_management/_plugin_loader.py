# plugin_loader.py
#
# Project: Mix Album
# License: GNU GPLv3
# Copyright (C) 2024 Róbert Čerňanský



import importlib
import pkgutil

from mix_album.plugins import providers, filters



class _PluginLoader:

    @staticmethod
    def loadProviders():
        for module in pkgutil.iter_modules(providers.__path__, providers.__name__ + "."):
            importlib.import_module(module.name)



    @staticmethod
    def loadFilterTypes():
        for module in pkgutil.iter_modules(filters.__path__, filters.__name__ + "."):
            importlib.import_module(module.name)
