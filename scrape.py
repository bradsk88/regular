import urlfetch
import os
import math
import re
from bs4 import BeautifulSoup

REMOVABLES = [
    "MONOLOGUE BY MR REGULAR",
    "NARRATION by MR REGULAR",
    "MONOLOGUE by MR. REGULAR",
    "MONOLOGUE by THE ROMAN",
    "OPENING NARRATION by MR. REGULAR",
    "OPENING NARRATION by THE ROMAN",
    "INTRO by MR REGULAR",
    "INTRO SONG by THE ROMAN",
    "INTRO by THE ROMAN",
    "OUTRO SONG by THE ROMAN",
]

def roundup(x):
    return int(math.ceil(x / 100.0)) * 100

def __main__():
    i = 0
    misses = 0
    huge_misses = 0
    while(True):
        if huge_misses > 5:
            return
        i += 1
        print("Fetching {}".format(i))
        res = urlfetch.fetch('http://regularquotes.com/episode/{}'.format(i))
        if res.status_code != 200:
            print("Status code was {}".format(res.status_code))
            misses += 1
            if misses > 10:
                misses = 0
                huge_misses += 1
                i = roundup(i) + 1
                print ("Moving on to {}".format(i))
            continue
        print('{} {}'.format(res.status_code, res.url))
        soup = BeautifulSoup(res.content, 'html.parser')
        found = soup.find('div', class_='epCol').get_text().replace('Transcript', '').replace('\n', ' ').replace('---', '--').strip()
        parts = found.split('--')
        for j, block in enumerate(parts):
            type = ' '.join(block[:40].split(' ')[:5]).upper()
            if 'There is no transcript for this episode yet. Maybe you could help us out?' in parts:
                continue
            priority_types = {
                'MONOLOGUE BY THE ROMAN': 'roman/main',
                'INTRO by THE ROMAN': 'roman/intro',
                'OUTRO SONG by THE ROMAN': 'roman/outro',
                'OPENING NARRATION by THE ROMAN': 'roman/intro',
                'MONOLOGUE': 'main',
                'INTRO SONG': 'roman/song', 
            }
            types = {
                'INTRO': 'intro', 
                'ROMAN': 'roman/main', 
                'OUTRO': 'outro', 
                'ENDING': 'outro', 
                'OPENING': 'intro',
            }
            finaltype = 'OTHER'
            print("Type is {}".format(type))
            for ts in [priority_types, types]:
                found = False
                for t, v in ts.items():
                    if t in type:
                        finaltype = v
                        found = True
                        break
                    else:
                        finaltype = 'main'
                if found:
                    break
            filename = '{}/{}-{}.txt'.format(finaltype, i, j)
            print("Writing to {}".format(filename))
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            for r in REMOVABLES:
                pattern = re.compile(r, re.IGNORECASE)
                block = pattern.sub('', block)
                pattern = re.compile('{}:'.format(r), re.IGNORECASE)
                block = pattern.sub('', block)
            with open(filename, 'w+') as f:
                f.write(block)
        print("Onward!!!!")

__main__()
