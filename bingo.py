"""
    Create Playlist and bingo cards from m3u playlist files.

    Usage:
        bingo.py  --srcfile=<srcfile> --numcards=<numcards> [--pdffile=<pdffile>]
        bingo.py  -h
        bingo.py  -v

    Options:
        -h,--help                       : show this help message
        -v, --version                   : show code version

    Arguments:
        --srcfile=<srcfile>             : source m3u file name
        --numcards=<numcards>           : integer number of bingo cards to produce
        --pdffile=<pdffile>             : PDF filename [default: playlist-bingo.pdf]

"""

# testing 1 2 3

# testing 4 5 6
import fnmatch
import os
import re
import json
import copy
import random
import render
import sys

from docopt import docopt

class Song:
    def __init__(self, artist, title):
        self.artist = artist
        self.title = title

    def __str__(self):
        return '{} - {}'.format(self.artist, self.title)


class Playlist:
    def __init__(self, title, order="title"):
        self._songs = []
        self.title = title
        self.order = order
        self.tags = []
        self.calendar = None

    def songs(self):
        return self._songs

    def get_randomized_songs(self):
        return np.random.shuffle(copy(self._songs))

    def add_song(self, song):
        self._songs.append(song)

#        for s in self._songs:


    def print_songs(self):
            print(s)

    def parse(self, infile):
        songRecordProg = re.compile('#EXTINF:\d+,(.*) - (.*)')

        for ln in infile.readlines():
            songMatch = songRecordProg.match(ln)
            if songMatch:
                (title, artist) = songMatch.groups()
                self.add_song(Song(artist, title))

        if not self._songs:
            raise Exception('Malformed playlist file : {}'.format(infile.name))


_title_re = re.compile('(\d+)\.\s*(.+)')


def _get_playlist_title_from_filename(filename):

    name = os.path.splitext(os.path.split(filename)[1])[0]
    title_match = _title_re.match(name)
    title = title_match.groups(1)[1] if title_match else name
    return title


def create_playlist(filename):
    with open(filename) as file:
        title = _get_playlist_title_from_filename(filename)
        print 'Processing file:{} title:{}'.format(filename, title)
        playlist = Playlist(title)
        playlist.parse(file)
        return playlist


def process_playlist_files(root, pattern='*.m3u'):
    fileNames = get_file_list_to_process(root, pattern)
    playlists = []

    for filename in fileNames:
        playlist = create_playlist(filename)
        # playlist.print_songs()
        playlists.append(playlist)

    return playlists


def get_file_list_to_process(root, pattern):
    fileList = []

    for dirpath, dirnames, filenames in os.walk(root):
        for filename in fnmatch.filter(filenames, pattern):
            fileList.append(os.path.join(dirpath, filename))

    return fileList


def create_random_songs_matrix(playlist, size=5):
    matrix = [[None for x in range(size)] for y in range(size)]
    songs = iter(random.sample(playlist.songs(), size * size))

    for row in range(size):
        for col in range(size):
            matrix[row][col] = next(songs)

    return matrix


def get_playlist_songs_distribution(playlist, matrices):
    song_map = dict([(song.title, {'artist': song.artist, 'count': 0}) for song in playlist.songs()])

    for matrix in matrices:
        for row in range(len(matrix)):
            for col in range(len(matrix[row])):
                song_map[matrix[row][col].title]['count'] += 1

    lst = [(key, value['artist'], value['count']) for key, value in song_map.items()]
    return sorted(lst, key=lambda item: item[2], reverse=True)


def create_bingo_cards(playlist, count, matrix_size=5):
    matrices = [create_random_songs_matrix(playlist, matrix_size) for n in range(count)]
    return matrices


def write_playlists(playlists, outname):
    with open(outname, 'w') as file:
        jsonstr = json.dump(playlists, file, default=lambda o: o.__dict__)


def main(docopt_args):
    try:
        srcfile = docopt_args['--srcfile']
        numcards = int(docopt_args['--numcards'])
        pdffile = docopt_args['--pdffile']

        playlist = create_playlist(srcfile)
        # playlist.printlist()
        # inpath = sys.argv[1]
        # dbpath = os.path.join(inpath, 'playlists.json')
        # playlists [process_playlist_files(inpath, '*.m3u')]
        # write_playlists(playlists, dbpath)
        matrices = create_bingo_cards(playlist, numcards)
        song_distribution = [pair for pair in get_playlist_songs_distribution(playlist, matrices)]
        render.create_bingo_cards_pdf(playlist.title, song_distribution, matrices, pdffile)

    except Exception as e:
        print "Error : ", e
        sys.exit(1)

if __name__ == '__main__':
    args = docopt(__doc__, version='Version 1.0')
    main(args)
