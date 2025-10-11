# audio_file_provider.py
#
# Project: Mix Album
# License: GNU GPLv3
# Copyright (C) 2024 - 2025 Róbert Čerňanský



import mimetypes
import os.path

import ffmpeg

from mix_album.app_context import AppContext
from mix_album.medium import Medium
from mix_album.abstract_provider import AbstractProvider
from mix_album.plugin_management.provider_repository import providerRepository



class AudioFileProvider(AbstractProvider):

    __CODEC_TO_EXTENSION_MAP = {
            'aac': '.m4a',
            'mp3': '.mp3',
            'opus': '.opus',
            'vorbis': '.ogg'
    }



    def __init__(self, appContext: AppContext):
        self.__appContext = appContext



    @property
    def specificity(self) -> int:
        return 0



    def provideMedia(self, descriptor: str) -> Medium:
        if self.__isVideoFile(descriptor):
            return Medium(self.__appContext, self.__extractAudio(descriptor))
        else:
            return Medium(self.__appContext, descriptor)



    def canHandle(self, descriptor: str) -> bool:
        return True



    @staticmethod
    def __isVideoFile(mediaFile: str) -> bool:
        return mimetypes.guess_type(mediaFile)[0].startswith("video")



    def __extractAudio(self, videoFilePath: str) -> str:
        audioStreamCodec = self.__getAudioStreamCodec(videoFilePath)
        audioFileName = self.__replaceExtension(
            os.path.basename(videoFilePath), self.__CODEC_TO_EXTENSION_MAP[audioStreamCodec])
        return self.__extractAudioToFile(videoFilePath, audioFileName)



    @staticmethod
    def __getAudioStreamCodec(videoFile: str) -> str:
        probeInfo = ffmpeg.probe(videoFile)
        audioStream = next((stream for stream in probeInfo["streams"] if stream["codec_type"] == "audio"))
        return audioStream["codec_name"]



    @staticmethod
    def __replaceExtension(fileName, extension) -> str:
        return f"{os.path.splitext(fileName)[0]}.{extension}"



    def __extractAudioToFile(self, videoFilePath: str, audioFileName: str) -> str:
        outputAudioFile = os.path.join(self.__appContext.tempDir, audioFileName)
        ffmpeg \
            .input(videoFilePath) \
            .output(outputAudioFile, vn = None, acodec = "copy") \
            .run(quiet = True)
        return outputAudioFile



providerRepository.registerProvider(AudioFileProvider)
