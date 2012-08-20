# -*- coding: cp1252 -*-
import re

import epguide

#compile regex objects here
re_fn1 = re.compile('[\w.]*?.[Ss]\\d\\d[Ee]\\d\\d')
re_fn1_t = re.compile('[Ss]\\d\\d[Ee]\\d\\d')
re_fn2 = re.compile('.*? \d{1,2}x\d{2}')
re_fn2_t = re.compile(' \d{1,2}x\d{2}')
#

def decodeFN(fn):
    """Attempts to decode a file name according to commonly used formatings.
    1:SHOW.NAME.SXXEXX.ENCODINGINFO (most common)
    2:SHOW NAME XxXX - TITLE (output format)
    else return (None,None,None,None)
    """
    if re_fn1.match(fn): #1
        titleend = re_fn1_t.search(fn).start()
        sn = fn[:titleend].replace('.',' ').strip().title()
        epid = fn[titleend:titleend+6]
        fformat = fn.split('.')[-1]
        season = int(epid[1:3])
        ep = int(epid[4:6])

    elif re_fn2.match(fn): #2
        match = re_fn2_t.search(fn)
        sn = fn[:match.start()].title()
        epid = fn[match.start()+1:match.end()]
        fformat = fn.split('.')[-1]
        season, ep = [int(i) for i in epid.split('x')]
        
    else: return (None,None,None,None)
    return (sn,season,ep,fformat)
    

def formatToOutput(sn,season,ep,fformat):
    try:
        epn = unicode(epguide.EpList[sn][season][ep], 'utf-8')
        epn = re.sub('[\/:*?"<>|]', '', epn)
        epn = re.sub('\u2019', '\'', epn)
    except KeyError:
        return ''
    s = str(season)
    e = str(ep).rjust(2,'0')
    return u'%s %sx%s - %s.%s' % (sn,s,e,epn,fformat)
