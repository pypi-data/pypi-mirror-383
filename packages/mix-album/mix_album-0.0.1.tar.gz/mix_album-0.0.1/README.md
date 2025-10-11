# Mix Album

Utility that helps to create a custom collection of songs - a mix album.


## Description

Let's describe a typical use case by example.  The result will be a directory with songs -- the *mix album* or
*mixtape*. 

First, create directory `Mix Album 01 (2024)`.  This will be our mix album.

_By default, the program assumes the name "Mix Album NN (YYYY)", where NN is the album number and YYYY is year in
which the album was established (current year).  So, first album (created in 2024) will be called
"Mix Album 01 (2024)", second album (let's say created in 2026) will be "Mix Album 02 (2026)", etc.  Please refer
to [Program Options](#program-options) or  [Configuration](#configuration) section to see how to customize the
album name._

To add a track (song) to the album one can point the program to an existing file or to a YouTube video ID.  To use a file enter following
command:

    $ mix-album-add --filter "metadata:artist=Example Artist;title=Example Song Title" example_song.mp3

This will create a copy of `example_song.mp3` file in the `Mix Album 01 (2024)` under the name
`01 - Example Artist - Example Song Title.mp3`.  The file will have metadata tags set. 

    Mix Album 01 (2024)
    `-- 01 - Example Artist A - Example Song Title.mp3

To add a song from YouTube specify YouTube video ID which is the 11 character long string in the video URL; the value of
`v` parameter.  In the following example URL the YouTube ID is 'xxxxxxxxxxx':
`https://www.youtube.com/watch?v=xxxxxxxxxxx`.

    $ mix-album-add --filter "metadata:artist=Example Artist B;title=Example YouTube Song Title;genre=Pop" xxxxxxxxxxx

After the command is successfully executed the album directory will contain the second track as well:

    Mix Album 01 (2024)
    |-- 01 - Example Artist A - Example Song Title.mp3
    `-- 02 - Example Artist B - Example YouTube Song Title.opus


### Handling More Albums

In case you want to stop adding song to the "Mix Album 01", simply create directory "Mix Album 02 (YYYY)" and new
songs will be added to the new album.  The general rule is that songs are added to the album with the highest
number.


## Filters

The application can modify the media file via set of filters.  First one, metadata, we have already used in the
previous example.  Besides that one there is also 'cut' and 'replay_gain'.

Syntax for each filter and its parameters is:

    --filter <filter_name>[:<paramerer1>=<value1>[;...]]


### Metadata Filter

It is used for setting the media metadata tags.  For example:

    $ mix-album-add --filter "metadata:artist=Example Artist A;title=Example Title;genre=Pop" ...


### Cut Filter

Removes parts from the start or the end of the media.  For example:

    $ mix-album-add --filter "cut:from=00:15;to=03:40" ...


### Replay Gain Filter

Sets the perceived volume of the media to a predefined level.  Example:

    $ mix-album-add --filter replay_gain ...


## Program Options

To see the complete list of the program options, run:

    $ mix-album-add --help


## Configuration

Configuration options are read by default from  `~/.config/mix_album/mix_album.conf` file.  It can contain following
options:

  - `albums-path`: path to the directory with mix albums (default: current directory)

  - `album-base-title`: Name of mix albums without number and year (default: Mix Album)

The file has to be in INI format with one section named `DEFAULT`.  Example of the configuration file:

    [DEFAULT]
    ; comment line
    albums-path = /path/to/media/library



## Installation

    pip install mix_album
