# youtube_provider.py
#
# Project: Mix Album
# License: GNU GPLv3
# Copyright (C) 2024 - 2025 Róbert Čerňanský



import os
import re

import yt_dlp

from mix_album.app_context import AppContext
from mix_album.medium import Medium
from mix_album.abstract_provider import AbstractProvider
from mix_album.plugin_management.provider_repository import providerRepository



class YoutubeProvider(AbstractProvider):

    def __init__(self, appContext: AppContext):
        self.__appContext = appContext



    @property
    def specificity(self) -> int:
        return 100



    def provideMedia(self, descriptor: str) -> Medium:
        audioFile = self.__downloadAudioFile(descriptor)
        return Medium(self.__appContext, audioFile)



    def canHandle(self, descriptor: str) -> bool:
        return re.match(r'^[^"&?\/\s]{11}$', descriptor)



    def __downloadAudioFile(self, youtubeId) -> str:
        downloadDir = self.__appContext.tempDir

        ytDlpOpts = {
            "format": "bestaudio",
            "postprocessors": [{
                "key": "FFmpegExtractAudio"
            }],
            "paths": {"home": f"{downloadDir}"}
        }
        with yt_dlp.YoutubeDL(ytDlpOpts) as ydl:
            try:
                errorCode = ydl.download(youtubeId)
            except Exception:
                errorCode = -1

        return os.path.join(downloadDir, self.__getDownloadedFileName(downloadDir)) if errorCode == 0 else ""



    @staticmethod
    def __getDownloadedFileName(directory: str) -> str:
        return os.listdir(directory)[0]



providerRepository.registerProvider(YoutubeProvider)
