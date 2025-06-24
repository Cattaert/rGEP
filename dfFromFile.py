# -*- coding: utf-8 -*-
"""
Created on Tue Jun 24 12:23:53 2025

@author: dcatt
"""

import pandas as pd
import tkinter


def readAnimatLabDir():
    filename = "animatlabSimDir.txt"
    try:
        f = open(filename, 'r')
        directory = f.readline()
        f.close()
    except Exception as e:
        print(e)
        directory = ""
    return directory

previousanimatsimdir = readAnimatLabDir()

root = tkinter.Tk()
root.withdraw()
res = tkinter.filedialog.askopenfilename(filetypes=(("csv files","*.csv"),
                                                        ("All files","*.*")))

root.destroy()

if len(res ) > 0:
    print("You chose %s" % res)


if type(res) == tuple:
    fname, __tmp = res
else:
    fname = res
print(fname)


df = pd.read_csv(fname)
