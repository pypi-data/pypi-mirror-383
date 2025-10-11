# filter_repository.py
#
# Project: Mix Album
# License: GNU GPLv3
# Copyright (C) 2024 - 2025 Róbert Čerňanský



from mix_album.abstract_filter import AbstractFilter



class FilterRepository:

    def __init__(self):
        self.__providers: list[type[AbstractFilter]] = []



    @property
    def filters(self) -> list[type[AbstractFilter]]:
        return self.__providers[:]



    def registerFilter(self, provider: type[AbstractFilter]):
        self.__providers.append(provider)



filterRepository = FilterRepository()
