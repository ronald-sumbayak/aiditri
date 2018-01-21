import os
import stat
import pprint

import mutagen.easyid3
import mutagen.id3
import mutagen.mp3
import sys
from mutagen.id3._frames import APIC

m = mutagen.id3.ID3 ('01 Did You Miss Me_.mp3')
m.setall ('APIC', [APIC (encoding = 3, mime = 'image/png', type = 3, data = open ('1.png', 'rb').read ())])
m.save (v2_version = 3)


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
        super (UnknownOptionError, self).__init__ ('pytagger: UnknownOptionError \'%s\'' % option)


class Tagger (object):
    artwork = None
    files = []
    tags = {}
    
    def open (self, filename):
        try:
            file = mutagen.easyid3.EasyID3 (filename)
        except mutagen.id3.ID3NoHeaderError:
            file = mutagen.File (filename, easy = True)
            file.add_tags ()
            file.save ()
        return file
    
    def print_tags (self):
        for f in self.files:
            file = self.open (f)
            print ()
            print ('File: \'' + f + '\'')
            print (file.pprint ())
    
    def retrieve_artwork (self, filename):
        m = mutagen.id3.ID3 (filename)
        apic = m.getall ('APIC')
        for i in range (len (apic)):
            with open (filename + ' (%d).png' % i, 'wb') as fuck:
                fuck.write (m.getall ('APIC')[0].data)
    
    def set_files (self, *args):
        self.files = args
    
    def set_tags (self, **kwargs):
        self.tags = kwargs
    
    def set_artwork (self, artwork):
        self.artwork = artwork
    
    def apply (self, clear_old=False, verbose=False):
        for f in self.files:
            if verbose:
                print ()
                print ('==========================================================================')
                print (f)
            
            file = self.open (f)
            self.retrieve_artwork (f)
            
            if verbose:
                print ('-------------------------------- ORIGINAL --------------------------------')
                print (file.pprint ())
                print ('--------------------------------   TAGS   --------------------------------')
                pprint.pprint (self.tags)
            
            if clear_old:
                file.clear ()
            
            file.update (self.tags)
            os.chmod (f, stat.S_IWRITE)
            file.save (v1 = 2, v2_version = 3)
            
            if verbose:
                print ('--------------------------------  RESULT  --------------------------------')
                print (file.pprint ())
            
            if self.artwork:
                if verbose:
                    print ('artwork=' + self.artwork)
                
                m = mutagen.id3.ID3 (f)
                m.setall ('APIC', [APIC (
                    encoding = 3,
                    mime = 'image/png',
                    type = 3,
                    data = open (self.artwork, 'rb').read ())])
                m.save (v2_version = 3)
            
            if verbose:
                print ('--------------------------------------------------------------------------')
        
        self.artwork = None
        self.files = []
        self.tags = []
        self.verbose = False
