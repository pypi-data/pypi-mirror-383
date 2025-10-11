# _mix_albums.py
#
# Project: Fresh Digital Add
# License: GNU GPLv3
# Copyright (C) 2024 Róbert Čerňanský



import fnmatch
import os
import re

from mix_album._mix_album import _MixAlbum



class _MixAlbums:

    def __init__(self, albumBaseName, albumsPath):
        self.__albumBaseName = albumBaseName
        self.__albumsPath = albumsPath
        self.__albumDirs = fnmatch.filter(os.listdir(self.__albumsPath), f"{self.__albumBaseName} *")



    def last(self) -> _MixAlbum:
        highestAlbumNumber = self.__count
        highestAlbumDir = next(filter(
            lambda albumDir: re.match(fr"{self.__albumBaseName} {highestAlbumNumber:02} \(\d{{4}}\)", albumDir),
            self.__albumDirs))
        return _MixAlbum(os.path.join(self.__albumsPath, highestAlbumDir))



    @property
    def __count(self) -> int:
        return len(self.__albumDirs)
