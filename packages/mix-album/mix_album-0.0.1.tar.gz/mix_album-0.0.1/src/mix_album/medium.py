# medium.py
#
# Project: Mix Album
# License: GNU GPLv3
# Copyright (C) 2024 - 2025 Róbert Čerňanský



import os.path
import shutil

import mutagen

from mix_album._metadata import _Metadata
from mix_album.app_context import AppContext



class Medium:

    def __init__(self, appContext: AppContext, mediaFile: str):
        self.__appContext = appContext
        self.__mediaFile = mediaFile
        self.__sourceFileName = os.path.basename(mediaFile)
        self.__fileExtension = os.path.splitext(mediaFile)[1][1:]



    def __bool__(self):
        return bool(self.mediaFile)



    def __str__(self):
        return self.mediaFile



    @property
    def mediaFile(self) -> str:
        return self.__mediaFile



    @property
    def sourceFileName(self) -> str:
        return self.__sourceFileName



    @property
    def fileExtension(self) -> str:
        return self.__fileExtension



    @property
    def metadata(self) -> _Metadata:
        audio = mutagen.File(self.mediaFile, easy = True)
        return _Metadata(
            title = audio.get("title")[0] if "title" in audio else None,
            artist = audio.get("artist")[0] if "artist" in audio else None,
            album = audio.get("album")[0] if "album" in audio else None,
            year = int(audio.get("date")[0]) if "date" in audio else None,
            trackNumber = int(audio.get("tracknumber")[0]) if "tracknumber" in audio else None,
            genre = audio.get("genre")[0] if "genre" in audio else None)
            # comment = audio.get("description")[0] if "description" in audio else None)



    def copy(self):
        mediaTempFileName = self.__appContext.generateTempFileName("medium", self.fileExtension)
        shutil.copyfile(self.mediaFile, mediaTempFileName)
        return self.cloneWithMediaFile(mediaTempFileName)



    def cloneWithMediaFile(self, mediaFile: str):
        clonedMedium = Medium(self.__appContext, mediaFile)
        clonedMedium.__sourceFileName = self.__sourceFileName
        return clonedMedium
