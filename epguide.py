"""Part of project: Show Renamer
Refer to main project file for details
"""

import urllib2
import cPickle
import time
import os
import re

#compile regex objects here
re_rows = re.compile('<tr[^>]*?id="brow".*?</table>.*?</tr>',re.M|re.S)
re_cells = re.compile('<td.*?> *?<a.*?>(.*?)</a> *?</td>',re.M|re.S)
#

def updateStatus(*args):
    """The parent script should overwrite this function with one
    that'll allow it to change the status bar in the window
    """
    pass 

def _dl_tvrage(show,season):
    """Given a show name and the season download a list of the episodes
    retrurning a dictionary sorted with ep no's as keys
    This code is designed to process pages from tvrage.com"""
    server = 'http://www.tvrage.com/'
    loca = show.replace(' ','_')+'/episode_list/'+str(season)
    response = urllib2.urlopen(server + loca)
    page = response.read()

    if response.getcode() != 200:
        print "show not found by name, going in by search page"
        """Some shows are inaccessable by their names instead they need
        to be accessed using an ID, this is retrievable from giving the
        showname to the sites search page and retrieving the first search
        result."""
        resultpage = urllib2.urlopen(server + 'search.php?search='+show).read()

        resultdivs = re.findall("<div id=\"show_search\".*>(.*?)</div>")
        showcode = re.findall("<a *?href='/(.*?)' *?>"+show, resultdivs[0], re.M|re.S|re.I)
        
        #id_ = re.findall("<a *?href='http://www.tvrage.com/shows/(.*?)' *?>"+show,idpage,re.M|re.S|re.I)
        if len(showcode)==0:
            return {}
            
        loca = showcode[0]+'/episode_list/'+str(season)
        response = urllib2.urlopen(server+loca)
        page = response.read()
        if response.getcode() != 200:
            return {}

    #get tables
    tables = re.findall("<table.*?class='b'.*?>(.*?)</table>", page, re.M|re.S|re.I)

    #get rows
    rows = re.findall("<tr.*?bgcolor.*?id=\"brow\".*?>(.*?)</tr>", tables[0], re.M|re.S|re.I)

    names = {}

    if rows:
        for row in rows:
            cells = re.findall("<td.*?>(.*?)</td>", row)

            epnumber = cells[0]
            epcode = re.findall("<a.*?>(.*?)</i></a>", cells[1])[0]
            epdate = cells[2]
            eptitle = re.findall("<a.*?>(.*?)</a>", cells[3])[-1]
            eprating = cells[4]


            seasonepnumber = epcode.split("x")[1]

            names[int(seasonepnumber)] = eptitle

#            print epcode + " - " + eptitle
            
    
##    rows = re_rows.findall(page)
##    names = {}
##    if not rows:
##        for row in rows:
##            #The second and third cells contain the information i need
##            cells = re_cells.findall(row)[1:3]
##            epno,epname = int(cells[0].split('x')[1][:2]), cells[1]
##
##            if epname.startswith("<img"):
##                lastbrak = epname[::-1].find(">")
##                epname = epname[-lastbrak:]
##
##            names[epno] = epname    

    return names



class _EpGuide:
    """This should be the object that holds each show"""
    def __init__(self):
        self.Listings = {}
        if os.path.exists('listings.pik'):
            self.Listings = cPickle.load(open('listings.pik'))

    def __getitem__(self,key):
        key = key.title()
        if key not in self.Listings:
            self.Listings[key] = EpGuide_Show(key,self)
        return self.Listings[key]

    def saveListings(self):
        cPickle.dump(self.Listings,open('listings.pik','w'))


class EpGuide_Show:
    """T"""
    validp =  86400 * 2 #validity period for listing 
    sources = {'tvrage':_dl_tvrage}
    source = 'tvrage' #Default source
    
    def __init__(self,showname,epg):
        self.epg = epg #nessesary to access pickler function
        self.Listing = {}
        self.sn = showname.title()

    def __getitem__(self,key):
        if key not in self.Listing or \
            self.Listing[key]['retr']+self.validp < time.time():
            updateStatus("Downloading stuff")
            self.Listing[key] = self.sources[self.source](self.sn,key)
            self.Listing[key]['retr'] = time.time()
            self.epg.saveListings()
        return self.Listing[key]

EpList = _EpGuide()
