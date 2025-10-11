# _provider_selector.py
#
# Project: Mix Album
# License: GNU GPLv3
# Copyright (C) 2024 Róbert Čerňanský



from mix_album.abstract_provider import AbstractProvider
from mix_album.app_context import AppContext
from mix_album.plugin_management._plugin_loader import _PluginLoader
from mix_album.plugin_management.provider_repository import providerRepository



class _ProviderSelector:

    def __init__(self, appContext: AppContext):
        self.__appContext = appContext



    def selectProvider(self, mediaDescriptor: str) -> AbstractProvider:
        _PluginLoader.loadProviders()

        for provider in reversed(sorted(map(lambda p: p(self.__appContext), providerRepository.providers))):
            if provider.canHandle(mediaDescriptor):
                return provider
