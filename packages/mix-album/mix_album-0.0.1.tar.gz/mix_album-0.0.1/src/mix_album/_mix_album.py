# _mix_album.py
#
# Project: Mix Album
# License: GNU GPLv3
# Copyright (C) 2024 - 2025 Róbert Čerňanský



import fnmatch
import os.path
import re
import shutil

from mix_album.medium import Medium



class _MixAlbum:

    def __init__(self, path):
        self.__path = path
        self.__title, self.__year = self.__parseDirName()



    @property
    def title(self) -> str:
        return self.__title



    @property
    def year(self) -> int:
        return self.__year



    def countTracks(self) -> int:
        return len(fnmatch.filter(os.listdir(self.__path), "[0-9][0-9] - *.*"))



    def addTrack(self, medium: Medium):
        title = medium.metadata.title if medium.metadata.title \
            else os.path.splitext(medium.sourceFileName)[0]
        fileName = f"{medium.metadata.trackNumber:02} - " + f"{medium.metadata.artist} - {title}.{medium.fileExtension}"
        shutil.copyfile(medium.mediaFile, os.path.join(self.__path, fileName))



    def __parseDirName(self) -> tuple[str, int]:
        match = re.match(fr"(.+ \d\d) \((\d{{4}})\)", os.path.basename(self.__path))
        return match.group(1), match.group(2)
