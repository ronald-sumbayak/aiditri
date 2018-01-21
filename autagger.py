import os
import re
import sys
import urllib.parse

import tagger

del sys.argv[0]

if len (sys.argv) == 0:
    sys.argv.append (os.getcwd ())

for arg in sys.argv:
    for dirpath, dirnames, filenames in os.walk (arg):
        mp3_file_count = len ([f for f in filenames if f.endswith ('.mp3')])
        if mp3_file_count > 0:
            pattern = r'\\(?P<albumartist>[\w ]+)\\\[(?P<date>[\d]+)\] (?P<album>[\w ]+)(?:\\disc-(?P<discnumber>[\d]+$))?'
            d = re.search (pattern, dirpath).groupdict ()
            
            albumartist = d['albumartist']
            date = d['date']
            album = d['album']
            discnumber = d.get ('discnumber')
            disctotal = len ([dir for dir in os.listdir (os.path.join (dirpath, '..'))])
            if not discnumber:
                discnumber = disctotal = '1'
            discnumber = int (discnumber)
            disctotal = int (disctotal)
            tracktotal = mp3_file_count
            
            for name in filenames:
                root, ext = os.path.splitext (name)
                
                if ext.lower () == '.mp3':
                    pattern = r'(?P<tracknumber>[\d]+) - (?:\[(?P<artists>.+)\] )?(?P<title>.+)'
                    m = re.match (pattern, root).groupdict ()
                    
                    tracknumber = int (m['tracknumber'])
                    artists = urllib.parse.unquote ((m.get ('artists') or albumartist)).split (', ')
                    title = m['title']
                    
                    tags = {
                        'albumartist': urllib.parse.unquote (albumartist),
                        'date': date,
                        'album': urllib.parse.unquote (album),
                        'discnumber': '%d/%s' % (discnumber, disctotal),
                        'tracknumber': '%d/%s' % (tracknumber, tracktotal),
                        'artist': artists,
                        'title': urllib.parse.unquote (title)}
                    
                    file = tagger.Tagger ()
                    file.set_files (os.path.join (dirpath, name))
                    file.set_tags (**tags)
                    
                    if 'cover.png' in filenames:
                        file.set_artwork (os.path.join (dirpath, 'cover.png'))
                    
                    file.apply (verbose = True, clear_old = True)
                    
                    artists = '[%s] ' % '; '.join (artists) if artists != [albumartist] else ''
                    new_filename = '%02d %s%s.mp3' % (int (tracknumber), artists, title)
                    new_filename = urllib.parse.quote (new_filename)
                    print (new_filename)
                    print ('==========================================================================')
                    os.rename (os.path.join (dirpath, name), os.path.join (dirpath, new_filename))
