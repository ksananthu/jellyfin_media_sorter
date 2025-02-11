# Jellyfin Media Sorter

Jellyfin Media Sorter is a tool designed to help you organize and manage your media files for use with Jellyfin, an open-source media server.

## Features

- Automatically sort and rename media files
- Support for movies, TV shows, and music
- Customizable sorting rules
- Integration with Jellyfin metadata

## Usage

1. Place your media files in the appropriate upload directories (`movies` for movies and `series` for series).
2. Each media folder should contain a `start.txt` file with the following format:
    ```
    cat [eg: ind, eng, oth]
    imdb url
    ```
