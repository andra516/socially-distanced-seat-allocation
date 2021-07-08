# -*- coding: utf-8 -*-
"""
Created on Wed Jul  7 12:46:32 2021

@author: henry

module containing functions that will handle file I/O when saving/loading seat
allocation sessions
"""

import numpy as np
import os
#import cv2
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
    # Create a new file at the directory path
    sessionNum = 1

    ## this is genuinely the most horrific way of doing things - I'm so sorry...
    while True:
        try:
            saveDirectory = directory + os.sep + 'Seat Allocation Session #' + str(sessionNum) + ' - ' + os.path.splitext(os.path.basename(PNGFilePath))[0]
            os.mkdir(saveDirectory)
#            print(saveDirectory)
            break
        except FileExistsError:
            sessionNum += 1
            continue
   
    PNGCopyFilePath = saveDirectory + os.sep + os.path.basename(PNGFilePath)
    shutil.copyfile(PNGFilePath, PNGCopyFilePath)
      
    ## SAVE SELECTED SEAT PIXEL COORDINATES
    seatPixelCoords = np.zeros(shape=(len(Xs),2))
    seatPixelCoords[:,0] = Xs
    seatPixelCoords[:,1] = Ys

    seatCoordFilePath = saveDirectory + os.sep + 'seatPixelCoords - Session #' + str(sessionNum) + '.txt'
    np.savetxt(seatCoordFilePath, seatPixelCoords)

    # (eventually) SAVE ALLOCATED SEAT COORDS/INDICES

    
    
    

def loadSession(directory):
    '''
    Function that loads the seatPixelCoords, the room plan .png (and eventually allocated seats)
    from given directory.
    
    Inputs:
        > directory: file path for directory previous session was saved in
        
    Returns:
        if folder contains what is expected:
        > PNGFilePath: file path of .png of room plan
        > seatPixelCoords: numpy ndarray of seat coordinates.
        if not:
        returns None indicating there was an error
    '''
    ### CHECK EXACTLY ONE .PNG AND ONE .TXT FILE - png will be image of lecture hall
    # txt will be seatPixelCoords
    numTXTs = 0
    numPNGs = 0
    numElse = 0
    for file in os.listdir(directory):
        if os.path.splitext(file)[1] == '.txt':
            numTXTs += 1
            coordsFile = file
        elif os.path.splitext(file)[1] == '.png':
            numPNGs += 1
            PNGFile = file
        else:
            numElse += 1
            
    if numTXTs != 1 or numPNGs != 1:
        print('File should only contain exactly one .png and one .txt file')
        return None
    
    seatCoordFilePath = directory + os.sep + coordsFile
    PNGFilePath = directory + os.sep + PNGFile
    
    seatPixelCoords = np.loadtxt(seatCoordFilePath)
    
    return (PNGFilePath, seatPixelCoords)







if __name__ == '__main__':
    directory = r'C:\Users\henry\Documents\Seat Allocation Project Sum 2021\Seat Allocation Project\GUI\Seat Allocation Session Save Data'
#    emptyFolder = r'C:\Users\henry\Documents\Seat Allocation Project Sum 2021\Seat Allocation Project\GUI\Seat Allocation Session Save Data\New Folder'

    PNGFilePath = r'C:\Users\henry\Documents\Seat Allocation Project Sum 2021\Seat Allocation Project\GUI\Seat Allocation Session Save Data\Full Seat Selection for Aston Webb Lower GFloor\Aston Webb C Block - Lower Ground Floor Plan.png'
    Xs = [10, 20, 30, 40, 50]
    Ys = [5, 10, 15, 20, 25]
    
    
    d = saveSession(directory, PNGFilePath, Xs, Ys)
    