# cut.py
#
# Project: Mix Album
# License: GNU GPLv3
# Copyright (C) 2024 - 2025 Róbert Čerňanský



import textwrap
import ffmpeg

from mix_album.abstract_filter import AbstractFilter
from mix_album.medium import Medium
from mix_album.plugin_management.filter_repository import filterRepository



class Cut(AbstractFilter):

    ARGUMENT_NAME = "cut"
    DESCRIPTION = "Cuts off the start and the end of the media at defined time stamps."
    ARGUMENT_HELP = textwrap.dedent("""
        from=<[HH:]MM:SS[.m]>  - Start cut from the given time stamp
        to=<[HH:]MM:SS[.m]>    - End cut at the given time stamp
        """)



    def __init__(self, appContext, argument, *_):
        self.__appContext = appContext
        self.__options = self.__parseArgument(argument)



    @classmethod
    def canParseArgument(cls, argument: str) -> bool:
        return argument.split(":")[0] == cls.ARGUMENT_NAME



    def apply(self, medium: Medium) -> Medium:
        return medium.cloneWithMediaFile(self.__cut(medium.mediaFile, medium.fileExtension))



    @staticmethod
    def __parseArgument(argument: str) -> dict[str, str]:
        options = {}
        argumentVars = argument[argument.index(":") + 1:]
        for keyValueStr in argumentVars.split(";"):
            key, value = keyValueStr.split("=")
            options[key] = value
        return options



    def __cut(self, inputMediaFile: str, fileExtension: str) -> str:
        outputMediaFile = self.__appContext.generateTempFileName("cut", fileExtension)

        inputArguments = {}
        if "from" in self.__options:
            inputArguments["ss"] = self.__options["from"]
        if "to" in self.__options:
            inputArguments["to"] = self.__options["to"]

        ffmpeg \
            .input(inputMediaFile, **inputArguments) \
            .output(outputMediaFile, codec = "copy") \
            .run()

        return outputMediaFile



filterRepository.registerFilter(Cut)
