# metadata.py
#
# Project: Mix Album
# License: GNU GPLv3
# Copyright (C) 2024 - 2025 Róbert Čerňanský



import textwrap
import mutagen

from mix_album._metadata import _Metadata
from mix_album._mix_album import _MixAlbum
from mix_album.abstract_filter import AbstractFilter
from mix_album.app_context import AppContext
from mix_album.medium import Medium
from mix_album.plugin_management.filter_repository import filterRepository



class Metadata(AbstractFilter):

    ARGUMENT_NAME: str = "metadata"
    DESCRIPTION: str = "Sets media metadata."
    ARGUMENT_HELP: str = textwrap.dedent("""
        title=<TITLE>    - Track title
        artist=<ARTIST>  - Artist name
        genre=<GENRE>    - Track genre
        """)



    def __init__(self, appContext: AppContext, argument: str, mixAlbum: _MixAlbum):
        self.__mixAlbum = mixAlbum
        self.__options = self.__parseArgument(argument)



    @classmethod
    def canParseArgument(cls, argument: str) -> bool:
        return argument.split(":")[0] == cls.ARGUMENT_NAME



    def apply(self, medium: Medium) -> Medium:
        mediumCopy = medium.copy()
        self.__setMetadata(mediumCopy, _Metadata(
            title = self.__options["title"], artist = self.__options["artist"], album = self.__mixAlbum.title,
            year = self.__mixAlbum.year, trackNumber = self.__mixAlbum.countTracks() + 1,
            genre = self.__options["genre"]))
        return mediumCopy



    @staticmethod
    def __parseArgument(argument: str) -> dict[str, str]:
        options = {}
        argumentVars = argument[argument.index(":") + 1:]
        for keyValueStr in argumentVars.split(";"):
            key, value = keyValueStr.split("=")
            options[key] = value
        return options



    @staticmethod
    def __setMetadata(medium: Medium, metadata: _Metadata):
        audio = mutagen.File(medium.mediaFile, easy = True)
        audio.delete()
        if metadata.title:
            audio["title"] = metadata.title
        if metadata.artist:
            audio["artist"] = metadata.artist
        if metadata.album:
            audio["album"] = metadata.album
        if metadata.year:
            audio["date"] = metadata.year
        if metadata.trackNumber:
            audio["tracknumber"] = str(metadata.trackNumber)
        if metadata.genre:
            audio["genre"] = metadata.genre
        # if metadata.comment:
        #     audio["description"] = metadata.comment
        audio.save()



filterRepository.registerFilter(Metadata)
