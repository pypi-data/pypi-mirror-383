# abstract_provider.py
#
# Project: Mix Album
# License: GNU GPLv3
# Copyright (C) 2024 Róbert Čerňanský



from abc import ABC, abstractmethod

from mix_album.medium import Medium



class AbstractProvider(ABC):

    def __eq__(self, other):
        return self.specificity == other.specificity



    def __lt__(self, other):
        return self.specificity < other.specificity



    @property
    @abstractmethod
    def specificity(self) -> int:
        pass



    @abstractmethod
    def provideMedia(self, descriptor: str) -> Medium:
        pass



    @abstractmethod
    def canHandle(self, descriptor: str) -> bool:
        pass
