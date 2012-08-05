"""Show Renamer
Project start: 19/01/2009
v0.1
Christopher Dudas <kristof.dudas@gmail.com>
This program is free to edit and redistribute under the condition that
I (Christopher Dudas) are given mention and I as author
take no responsibility for whatever damage this file may cause.
"""

import os
import tkFileDialog
import re
from Tkinter import *
import threading
import Queue

import dataworker


#global data here
files = {} #files[old] = new
d = ''
parse = Queue.Queue()
#


def renFiles():
    """Accepts a directory and a list of tuples in the form (oldname,newname).
    Renames files according to the tuples in the directory"""
    global files, d
    if not d.endswith('/') or d.endswith('\\'):
        d += '\\'
    for i in files:
        print d + i + " => " + d + files[i]
        os.rename(d + i, d + files[i])
        

def decoderThread():
    while parse.empty()==False:
        job = parse.get()
        print job
        dec = dataworker.decodeFN(job[1])
        print dec
        if dec==(None,None,None,None):
            updateItem(job[0],'   ---Invalid---')
            continue
        out = dataworker.formatToOutput(*dec)
        if out=='':
            updateItem(job[0],'   ---Invalid---')
            continue
        files[job[1]] = out
        updateItem(job[0],out)
        
    b2.config({'state':'normal'})
    


def changeWorkingDirectory():
    global d, files

    files = {}
    
    d = tkFileDialog.askdirectory()

    b2.config({'state':'disabled'})
    dBox.config({'state':'normal'})
    dBox.delete(0,'end')
    dBox.insert(0,d)
    dBox.config({'state':'disabled'})

    #here populate the first list with the files
    list1.delete(0,END)
    list2.delete(0,END)

    n = 0
    for i in os.listdir(d):
        if os.path.isdir(d+"\\"+i): continue
        list1.insert(END,i)
        list2.insert(END,"   ---Working---")
        parse.put((n,i))
        n+=1
        
    thr = threading.Thread(target=decoderThread)
    thr.start()
        




def updateItem(num,text):
    list2.delete(num)
    list2.insert(num,text)
    

def setListsY(*args):
    list1.yview(*args)
    list2.yview(*args)

def setScrollbar1(*args):
    scrollbar.set(*args)
    #list2.yview(*args)
    list2.yview('scroll', '1', 'pages')

def setScrollbar2(*args):
    scrollbar.set(*args)
    #list1.yview(*args)
    list1.yview('scroll', '1', 'pages')
    
def correctListsY():
    list2.yview(list1.yview)


def setStatus(txt):
    staus.set(txt)


####Start GUI coding
root = Tk()

#main:
r1 = Frame(root)
r2 = Frame(root)
r3 = Frame(root)

    #-row1:
dBox_l = Label(r1,text='Select directory to parse:')
dBox = Entry(r1,state='disabled')
dBoxButton = Button(r1,text='Browse',command=changeWorkingDirectory)

dBox_l.pack(side=LEFT)
dBox.pack(side=LEFT)
dBoxButton.pack(side=LEFT)
    #-/

    #-row2:
r2_1 = Frame(r2)
r2_2 = Frame(r2)
r2_3 = Frame(r2,cnf={'padx':'10'})

scrollbar = Scrollbar(master=r2_2,command=setListsY)
scrollbar.pack(side=RIGHT,fill=Y)

        #--row2-col1
list1label = Label(r2_1,text='File to be renamed:')
list1 = Listbox(master=r2_1,selectmode=EXTENDED,yscrollcommand=setScrollbar1,
                cnf={'width':'35','height':'35'})

list1label.pack()
list1.pack(side=LEFT)
        #--/

        #--row2-col2
list2label = Label(r2_2, text='Preview output:')
list2 = Listbox(master=r2_2,state=NORMAL,yscrollcommand=setScrollbar2,
                cnf={'width':'35','height':'35'})

list2label.pack()
list2.pack(side=LEFT)
        #--/

        #--row2-col3
#b1 = Button(r2_3,text='Make Preview',command=generatePreview)
b2 = Button(r2_3,text='Commit',command=renFiles)

#b1.pack()
b2.pack()
        #--/

r2_1.pack(side=LEFT)
r2_2.pack(side=LEFT)
r2_3.pack(side=LEFT)
    #-/

    #-row3
status = StringVar()
status.set("Show Renamer v1.0 by Christopher Dudas")
sbar = Label(r3, textvariable=status, bd=1, anchor=W, relief=SUNKEN)
sbar.pack(side=BOTTOM, fill=X)
    #-/

r1.pack()
r2.pack()
r3.pack(fill=X)
#/

root.mainloop()
