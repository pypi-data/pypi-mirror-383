# app_context.py
#
# Project: Mix Album
# License: GNU GPLv3
# Copyright (C) 2024 - 2025 Róbert Čerňanský



import os
import tempfile
import uuid



class AppContext:

    def __init__(self):
        self.__tempDir = None



    def __enter__(self):
        return self



    def __exit__(self, exceptionType, exceptionVal, exceptionTraceback):
        if self.__tempDir:
            self.__tempDir.cleanup()
            self.__tempDir = None



    @property
    def tempDir(self) -> str:
        if not self.__tempDir:
            self.__tempDir = tempfile.TemporaryDirectory(prefix = "mix_album_")
        return self.__tempDir.name



    def generateTempFileName(self, prefix, extension) -> str:
        return os.path.join(self.tempDir, f"{prefix}_{uuid.uuid4()}.{extension}")
