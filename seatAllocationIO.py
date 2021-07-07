# -*- coding: utf-8 -*-
"""
Created on Wed Jul  7 12:46:32 2021

@author: henry

module containing functions that will handle file I/O when saving/loading seat
allocation sessions
"""

import numpy as np
import os
import shutil



def saveSession(directory, PNGFilePath, Xs, Ys):
    '''
    Function that saves the progress made in selecting seats in a given room plan.
    
    - Saves a copy of the room plan .png which seats have been placed onto to new folder specific to that room and attempt/session
    - Saves a numpy array of seat coordinates (in pixels on the .png) to a .txt file named : 'seatPixelCoords - Session #{num}.txt'
    - Eventually will also save indices of selected seats which have been chosen for the allocation to a seperate .txt file
    
    Inputs:\n
        > directory, str of directory path new folder should be created within.\n
        > PNGFilePath, str of the seating plan .png file path.\n
        > Xs - list of floats of all X coordinates (in pixel space) of selected seats to be saved.\n
        > Ys - list of floats.\n
    
    '''
#    print(directory, '\n', PNGFilePath,'\n', Xs,'\n', Ys)
    # Create a new file at the directory path
    sessionNum = 1
    
    ## this is genuinely the most horrific way of doing things - I'm so sorry
    while True:
        try:
            saveDirectory = directory + '\\Seat Allocation Session #' + str(sessionNum) + ' - ' + os.path.splitext(os.path.basename(PNGFilePath))[0]
            os.mkdir(saveDirectory)
            break
        except FileExistsError:
            sessionNum += 1
            continue
    ## SAVE COPY OF .PNG TO NEW SAVEDIRECTORY
    shutil.copy(PNGFilePath, saveDirectory)
    
    ## SAVE SELECTED SEAT PIXEL COORDINATES
    seatPixelCoords = np.zeros(shape=(len(Xs),2))
    seatPixelCoords[:,0] = Xs
    seatPixelCoords[:,1] = Ys

    seatCoordFilePath = saveDirectory + '\\seatPixelCoords - Session #' + str(sessionNum) + '.txt'
    np.savetxt(seatCoordFilePath, seatPixelCoords)

    ## (eventually) SAVE ALLOCATED SEAT COORDS/INDICES
                
    
    
    

def loadSession():
    pass


if __name__ == '__main__':
    directory = r'C:\Users\henry\Documents\Seat Allocation Project Sum 2021\Seat Allocation Project\GUI\testing saving'
    PNGFilePath = r'C:\Users\henry\Documents\Seat Allocation Project Sum 2021\Seat Allocation Project\GUI\Room Plans\Aston Webb C Block - Lower Ground Floor Plan.pdf-Page1.png'
    Xs = [10, 20, 30, 40, 50]
    Ys = [5, 10, 15, 20, 25]
    saveSession(directory, PNGFilePath, Xs, Ys)