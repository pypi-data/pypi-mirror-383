# _metadata.py
#
# Project: Mix Album
# License: GNU GPLv3
# Copyright (C) 2024 Róbert Čerňanský



class _Metadata:

    def __init__(self, title: str = None, artist: str = None, album: str = None, year: int = 0, trackNumber: int = 0,
                 genre: str = None, comment: str = None):
        self.__title = title
        self.__artist = artist
        self.__album = album
        self.__year = year
        self.__trackNumber = trackNumber
        self.__genre = genre
        self.__comment = comment



    @property
    def title(self) -> str:
        return self.__title


    @property
    def artist(self) -> str:
        return self.__artist



    @property
    def album(self) -> str:
        return self.__album



    @property
    def year(self) -> int:
        return self.__year



    @property
    def trackNumber(self) -> int:
        return self.__trackNumber



    @property
    def genre(self) -> str:
        return self.__genre



    @property
    def comment(self) -> str:
        return self.__comment
