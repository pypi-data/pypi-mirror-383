# provider_repository.py
#
# Project: Mix Album
# License: GNU GPLv3
# Copyright (C) 2024 Róbert Čerňanský



from mix_album.abstract_provider import AbstractProvider



class ProviderRepository:

    def __init__(self):
        self.__providers: list[type[AbstractProvider]] = []



    @property
    def providers(self) -> list[type[AbstractProvider]]:
        return self.__providers[:]



    def registerProvider(self, provider: type[AbstractProvider]):
        self.__providers.append(provider)



providerRepository = ProviderRepository()
