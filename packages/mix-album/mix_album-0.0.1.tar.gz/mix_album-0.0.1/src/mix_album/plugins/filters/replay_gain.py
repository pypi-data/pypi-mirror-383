# replay_gain.py
#
# Project: Mix Album
# License: GNU GPLv3
# Copyright (C) 2024 - 2025 Róbert Čerňanský



import json
import re

import ffmpeg

from mix_album.abstract_filter import AbstractFilter
from mix_album.medium import Medium
from mix_album.plugin_management.filter_repository import filterRepository



class ReplayGain(AbstractFilter):

    ARGUMENT_NAME: str = "replay_gain"
    DESCRIPTION: str = "Sets loudness to a predefined value."
    ARGUMENT_HELP: str = ""

    __LOUDNORM_PARAM_I = -12
    __LOUDNORM_PARAM_LRA = 20
    __LOUDNORM_PARAM_TP = 0

    __I_TOLERANCE = 2

    __OUTPUT_FILE_EXTENSION = "mp3"



    def __init__(self, appContext, *_):
        self.__appContext = appContext



    @classmethod
    def canParseArgument(cls, argument: str) -> bool:
        return argument.split(":")[0] == cls.ARGUMENT_NAME



    def apply(self, medium: Medium) -> Medium:
        measuredSoundParameters = self.__measureSoundParameters(medium.mediaFile)
        if self.__isLoudnessSimilarToDesired(measuredSoundParameters):
            return medium
        else:
            return medium \
                .cloneWithMediaFile(self.__applyLoudnessNormalization(medium.mediaFile, measuredSoundParameters))



    @classmethod
    def __measureSoundParameters(cls, inputMediaFile: str) -> dict[str, str]:
        _, outputText = ffmpeg \
            .input(inputMediaFile) \
            .filter("loudnorm", I = cls.__LOUDNORM_PARAM_I, TP = cls.__LOUDNORM_PARAM_TP, LRA = cls.__LOUDNORM_PARAM_LRA,
                    print_format = "json") \
            .output("-", format = "null") \
            .run(capture_stderr = True)
        measuredLoudNormValuesJson = re.search("(?<=Parsed_loudnorm_).+(?={)(.+})", str(outputText)[:-1]).groups()[0]
        return json.loads(measuredLoudNormValuesJson.replace("\\n", "").replace("\\t", ""))



    def __applyLoudnessNormalization(self, inputMediaFile: str, soundParameters: dict[str, str]) -> str:
        outputMediaFile = self.__appContext.generateTempFileName("replay_gain", self.__OUTPUT_FILE_EXTENSION)
        ffmpeg \
            .input(inputMediaFile)\
            .filter("loudnorm",
                    I = self.__LOUDNORM_PARAM_I,
                    TP = self.__LOUDNORM_PARAM_TP,
                    LRA = self.__LOUDNORM_PARAM_LRA,
                    measured_I = soundParameters["input_i"],
                    measured_TP = soundParameters["input_tp"],
                    measured_LRA = soundParameters["input_lra"],
                    measured_thresh = soundParameters["input_thresh"])\
            .output(outputMediaFile, map_metadata = ["0", "0:s:0"], movflags = True)\
            .run(quiet = True)
        return outputMediaFile



    def __isLoudnessSimilarToDesired(self, soundParameters: dict[str, str]) -> bool:
        return abs(float(soundParameters["input_i"]) - self.__LOUDNORM_PARAM_I) < self.__I_TOLERANCE



filterRepository.registerFilter(ReplayGain)
