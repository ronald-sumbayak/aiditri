import os
import pprint
import stat

from mutagen import File
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, ID3NoHeaderError
from mutagen.id3._frames import APIC

help_text = (
    '\n'
    '-h --help        show this screen\n'
    '-a --albumartist\n'
    '-p --artist\n'
    '-A --album\n'
    '-t --title\n'
    '-g --genre\n'
    '-y --date\n'
    '-T --tracknumber X or X/Y (song number/total)\n'
    '-d --discnumber  X or X/Y (disc number/total)\n'
    '-v --verbose     display tags before and after edit for each file\n'
)

tag_list = [
    ('a', 'albumartist'),
    ('p', 'artist'),
    ('A', 'album'),
    ('t', 'title'),
    ('g', 'genre'),
    ('y', 'date'),
    ('T', 'tracknumber'),
    ('d', 'discnumber')
]


class UnknownOptionError (Exception):
    def __init__ (self, option):
        super ().__init__ ('tagger: UnknownOptionError \'%s\'' % option)


class UnknownTagError (Exception):
    def __init__ (self, tag):
        super ().__init__ ('tagger: UnknownTagError \'%s\'' % tag)


class Tagger (object):
    __filename: str = None
    __artwork: str = None
    __file_easy: EasyID3 = None
    __file: ID3 = None
    __tags: dict = {}
    __available_tags: list = [tag for _, tag in tag_list]
    
    def __init__ (self, filename, artwork=None, **kwargs):
        self.__filename = filename
        self.__artwork = artwork
        for tag in kwargs:
            if tag not in self.__available_tags:
                raise UnknownTagError (tag)
        self.open ()
    
    def open (self):
        try:
            file_easy = EasyID3 (self.__filename)
        except ID3NoHeaderError:
            file_easy = File (self.__filename, easy = True)
            file_easy.add_tags ()
            file_easy.save ()
        self.__file_easy = file_easy
        self.__file = ID3 (self.__filename)
    
    def print_tags (self):
        print ()
        print ('File: \'' + self.__filename + '\'')
        print (self.__file_easy.pprint ())
    
    def extract_artwork (self):
        apic = self.__file.getall ('APIC')
        for i in range (len (apic)):
            with open (self.__filename + ' (%d).png' % i, 'wb') as fuck:
                fuck.write (self.__file.getall ('APIC')[0].data)
    
    def clear_tags (self):
        self.__file_easy.clear ()
    
    def set (self, tag, value):
        if tag not in self.__available_tags:
            raise UnknownTagError (tag)
        self.__tags[tag] = value
    
    def set_artwork (self, artwork):
        self.__artwork = artwork
    
    def apply (self, verbose=False):
        if verbose:
            print ()
            print ('==========================================================================')
            print (self.__filename)
        
        if verbose:
            print ('-------------------------------- ORIGINAL --------------------------------')
            print (self.__file_easy.pprint ())
            print ('--------------------------------   TAGS   --------------------------------')
            pprint.pprint (self.__tags)
        
        self.__file_easy.update (self.__tags)
        
        if self.__artwork:
            self.__file.setall ('APIC', [APIC (
                encoding = 3,
                mime = 'image/png',
                type = 3,
                data = open (self.__artwork, 'rb').read ())])

        os.chmod (self.__filename, stat.S_IWRITE)  # set writable
        self.__file_easy.save (v1 = 2, v2_version = 3)
        self.__file.save (v2_version = 3)
        
        if verbose:
            print ('--------------------------------  RESULT  --------------------------------')
            print (self.__file_easy.pprint ())
        
        if self.__artwork:
            if verbose:
                print ('artwork=' + self.__artwork)
        
        if verbose:
            print ('--------------------------------------------------------------------------')

        self.__filename = None
        self.__artwork = None
        self.__file_easy = None
        self.__file = None
        self.__tags = {}
