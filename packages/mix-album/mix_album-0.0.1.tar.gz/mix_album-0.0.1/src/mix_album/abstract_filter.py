# abstract_filter.py
#
# Project: Mix Album
# License: GNU GPLv3
# Copyright (C) 2024 - 2025 Róbert Čerňanský



from abc import ABC, abstractmethod

from mix_album.medium import Medium



class AbstractFilter(ABC):

    ARGUMENT_NAME: str = None
    DESCRIPTION: str = None
    ARGUMENT_HELP: str = None



    @abstractmethod
    def canParseArgument(cls, argument: str) -> bool:
        pass



    @abstractmethod
    def apply(self, medium: Medium) -> Medium:
        pass
