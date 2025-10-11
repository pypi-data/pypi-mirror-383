# main.py
#
# Project: Mix Album
# License: GNU GPLv3
# Copyright (C) 2024 - 2025 Róbert Čerňanský



import argparse
import configparser
import os
import shutil
import sys
import textwrap

from mix_album import __version__
from mix_album._mix_albums import _MixAlbums
from mix_album._provider_selector import _ProviderSelector
from mix_album.app_context import AppContext
from mix_album.plugin_management._plugin_loader import _PluginLoader
from mix_album.plugin_management.filter_repository import filterRepository



def main():
    _PluginLoader.loadFilterTypes()
    args = __parseArgumentsAndConfiguration()

    with AppContext() as appContext:
        mixAlbum = _MixAlbums(args.album_base_title, args.albums_path).last()
        medium = _ProviderSelector(appContext).selectProvider(args.media).provideMedia(args.media)
        if medium:
            filters = __createFilters(args.filter, filterRepository.filters, appContext, mixAlbum)
            for filterInstance in filters:
                medium = filterInstance.apply(medium)

            mixAlbum.addTrack(medium)
        else:
            print("No track added.")
            sys.exit(1)



def __parseArgumentsAndConfiguration() -> argparse.Namespace:
    preArgumentParser = argparse.ArgumentParser(add_help = False)
    preArgumentParser.add_argument(
        "--config-file-path", default = os.path.expanduser("~/.config/mix_album/mix_album.conf"))
    preArgs, remainingArgs = preArgumentParser.parse_known_args()

    configParser = configparser.ConfigParser()
    configParser.read(preArgs.config_file_path)
    configSection = configParser["DEFAULT"]

    argumentParser = argparse.ArgumentParser(
        description = textwrap.fill("Utility that helps to create a custom collection of songs - a mix album.",
                                    shutil.get_terminal_size().columns),
        formatter_class = argparse.RawDescriptionHelpFormatter)
    argumentParser.add_argument("media", help = "Media that shall be added.")
    argumentParser.add_argument("--albums-path", default = configSection.get("albums-path", "."),
                                help = "Path with mix albums.")
    argumentParser.add_argument("--album-base-title", default = configSection.get("album-base-title", "Mix Album"),
                                help = "Title of the mix album without number and year.")
    argumentParser.add_argument("-f", "--filter", action = "append",
                                help = "Filter which shall run on media. Can be specified multiple times.")
    argumentParser.add_argument("--version", action = "version", version = f"Mix Album ver. {__version__}")

    argumentParser.add_argument_group("Filters", "")

    for filterType in filterRepository.filters:
        argumentParser.add_argument_group(filterType.ARGUMENT_NAME,
                                          filterType.DESCRIPTION + "\n" + filterType.ARGUMENT_HELP)

    return argumentParser.parse_args(remainingArgs)



def __createFilters(filtersArguments: str, availableFilterTypes, appContext, mixAlbum):
    for filterArgument in filtersArguments:
        created = False
        for filterType in availableFilterTypes:
            if filterType.canParseArgument(filterArgument):
                yield filterType(appContext, filterArgument, mixAlbum)
                created = True
        if not created:
            print(f"Unknown filter '{filterArgument}'.")
            sys.exit(-1)
